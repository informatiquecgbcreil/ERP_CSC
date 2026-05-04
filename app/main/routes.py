from pathlib import Path
import re
import csv
from io import StringIO, BytesIO
from datetime import date
from time import perf_counter

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
from sqlalchemy import func


def _parse_iso_date(s: str):
    try:
        if not s:
            return None
        return date.fromisoformat(s)
    except Exception:
        return None

def _indicator_date_range(params: dict, selected_annee: int | None):
    period = (params.get("period") or "context").strip()
    if period == "custom":
        d1 = _parse_iso_date(params.get("start") or "")
        d2 = _parse_iso_date(params.get("end") or "")
        if d1 and d2 and d2 < d1:
            d1, d2 = d2, d1
        return d1, d2
    if period == "year" or period == "context":
        if selected_annee:
            return date(selected_annee, 1, 1), date(selected_annee, 12, 31)
    return None, None

def _indicator_target_status(value, target, op: str):
    if target is None or value is None:
        return None
    try:
        v = float(value)
        t = float(target)
    except Exception:
        return None
    if t == 0:
        return None
    op = (op or "ge").strip()

    # ge : on veut v >= t ; le : on veut v <= t
    if op == "le":
        ratio = t / v if v != 0 else float("inf")
        ok = v <= t
    else:
        ratio = v / t
        ok = v >= t

    if ok:
        return "ok"
    if ratio >= 0.75:
        return "warn"
    return "bad"
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash,
    abort, current_app, Response, jsonify, send_file, session
)
import unicodedata
from flask_login import login_required, current_user
from app.rbac import require_perm, can, can_access_secteur

from app.extensions import db
from app.models import (
    Subvention,
    LigneBudget,
    Depense,
    Projet,
    SubventionProjet,
    AtelierActivite,
    SessionActivite,
    PresenceActivite,
    ProjetAtelier,
    ProjetIndicateur,
    Participant,
    Partenaire,
    Quartier,
    MaterielType,
    MaterielConsommationConfig,
    MaterielConsommationLigne,
)
from app.previsionnel.referentiel import BudgetCategorieReferentiel, BudgetCompteReferentiel
from app.services.dashboard_service import build_dashboard_context
from app.services.dashboard_customization import (
    available_quick_actions,
    available_widgets,
    load_dashboard_pref,
    reset_dashboard_pref,
    save_dashboard_pref,
)

bp = Blueprint("main", __name__)

SEARCH_TYPE_PRIORITY = {
    "Participant": 0,
    "Quartier": 1,
    "Projet": 2,
    "Subvention": 3,
    "Atelier": 4,
    "Partenaire": 5,
}

SEARCH_TYPE_ALIASES = {
    "participant": "Participant",
    "participants": "Participant",
    "usager": "Participant",
    "usagers": "Participant",
    "quartier": "Quartier",
    "quartiers": "Quartier",
    "zone": "Quartier",
    "zones": "Quartier",
    "projet": "Projet",
    "projets": "Projet",
    "subvention": "Subvention",
    "subventions": "Subvention",
    "financement": "Subvention",
    "financements": "Subvention",
    "atelier": "Atelier",
    "ateliers": "Atelier",
    "activité": "Atelier",
    "activite": "Atelier",
    "activités": "Atelier",
    "activites": "Atelier",
    "partenaire": "Partenaire",
    "partenaires": "Partenaire",
}


def _normalize_search_text(value: str | None) -> str:
    raw = (value or "").strip().lower()
    if not raw:
        return ""
    return "".join(ch for ch in unicodedata.normalize("NFKD", raw) if not unicodedata.combining(ch))


def _parse_search_query(term: str) -> dict:
    raw_parts = [tok.strip() for tok in (term or "").split() if tok.strip()]
    parsed = {"type_filter": None, "secteur_filter": None, "quartier_filter": None, "tokens": []}
    for part in raw_parts:
        low = part.lower()
        if low.startswith("type:"):
            parsed["type_filter"] = (part.split(":", 1)[1] or "").strip().lower() or None
            continue
        if low.startswith("secteur:"):
            parsed["secteur_filter"] = (part.split(":", 1)[1] or "").strip() or None
            continue
        if low.startswith("quartier:"):
            parsed["quartier_filter"] = (part.split(":", 1)[1] or "").strip() or None
            continue
        parsed["tokens"].append(part)
    return parsed


def _run_global_search(term: str, *, panel_limit: int = 20, page_limit: int = 100):
    start_ts = perf_counter()
    term = (term or "").strip()
    if len(term) < 2:
        return {"results": [], "query": term, "facets": {"types": {}, "secteurs": {}}, "debug": {"duration_ms": 0}}

    parsed = _parse_search_query(term)
    sql_tokens = [tok.strip().lower() for tok in parsed["tokens"] if tok.strip()]
    tokens = [_normalize_search_text(tok) for tok in sql_tokens if _normalize_search_text(tok)]
    if not tokens or not sql_tokens:
        return {"results": [], "query": term, "facets": {"types": {}, "secteurs": {}}, "debug": {"duration_ms": 0}}

    type_filter = parsed["type_filter"]
    secteur_filter = (parsed["secteur_filter"] or "").strip()
    quartier_filter = _normalize_search_text(parsed["quartier_filter"] or "")

    has_global_scope = can("scope:all_secteurs")
    user_secteur = (getattr(current_user, "secteur_assigne", "") or "").strip()
    if secteur_filter and (not has_global_scope) and secteur_filter.lower() != user_secteur.lower():
        return {"results": [], "query": term, "facets": {"types": {}, "secteurs": {}}, "debug": {"duration_ms": 0}}

    active_secteur_filter = secteur_filter or (None if has_global_scope else user_secteur)
    wanted_type = SEARCH_TYPE_ALIASES.get(type_filter or "")
    dialect_name = ((db.session.bind.dialect.name if db.session.bind else "") or "").lower()
    results: list[dict] = []
    candidate_limit = max(panel_limit, min(max(page_limit, 20), 120))
    fetch_limit = max(candidate_limit * 3, 24)

    def _like(column, pattern: str):
        if dialect_name == "postgresql":
            return db.func.coalesce(column, "").ilike(pattern)
        return db.func.lower(db.func.coalesce(column, "")).like(pattern.lower())

    def _token_mode_clause(columns, token: str, mode: str):
        if mode == "exact":
            return db.or_(*[_like(col, token) for col in columns])
        if mode == "prefix":
            patterns = (f"{token}%", f"% {token}%", f"%-{token}%")
            return db.or_(*[_like(col, pattern) for col in columns for pattern in patterns])
        return db.or_(*[_like(col, f"%{token}%") for col in columns])

    def _filter_for_tokens(columns, *, mode: str):
        source_tokens = sql_tokens if mode in {"exact", "prefix", "contains"} else tokens
        return db.and_(*[_token_mode_clause(columns, token, mode) for token in source_tokens])

    def _run_ranked_rows(base_query, columns, order_by, *, row_id_attr="id"):
        selected = []
        seen_ids = set()
        for mode in ("exact", "prefix", "contains"):
            needed = fetch_limit - len(selected)
            if needed <= 0:
                break
            q = base_query.filter(_filter_for_tokens(columns, mode=mode))
            if seen_ids:
                q = q.filter(~getattr(base_query.column_descriptions[0]["entity"], row_id_attr).in_(seen_ids))
            rows = q.order_by(*order_by).limit(needed).all()
            for row in rows:
                row_id = getattr(row, row_id_attr, None)
                if row_id in seen_ids:
                    continue
                seen_ids.add(row_id)
                selected.append(row)
        return selected

    token_phrase = " ".join(tokens)

    def _score_item(label: str | None, meta: str | None, *extras: str | None) -> int:
        bag = " ".join([label or "", meta or "", *[x or "" for x in extras]])
        bag_low = _normalize_search_text(bag)
        label_low = _normalize_search_text(label)
        meta_low = _normalize_search_text(meta)
        score = 0
        if token_phrase and token_phrase in label_low:
            score += 110
        if token_phrase and token_phrase in bag_low:
            score += 35
        for token in tokens:
            if label_low == token:
                score += 180
            if label_low.startswith(token):
                score += 80
            if f" {token}" in label_low or f"-{token}" in label_low:
                score += 30
            if token in label_low:
                score += 40
            if token in meta_low:
                score += 16
            if token in bag_low:
                score += 12
        score += max(0, 30 - max(0, len(label_low) - len(token_phrase or label_low)))
        return score

    if (wanted_type in {None, "Participant"}) and (can("participants:view") or can("participants:view_all")):
        participants_q = Participant.query.outerjoin(Quartier, Quartier.id == Participant.quartier_id)
        if quartier_filter:
            participants_q = participants_q.filter(
                db.or_(
                    _like(Quartier.nom, f"%{quartier_filter}%"),
                    _like(Quartier.ville, f"%{quartier_filter}%"),
                )
            )
        if active_secteur_filter:
            has_presence_in_user_secteur = (
                db.session.query(PresenceActivite.id)
                .join(SessionActivite, SessionActivite.id == PresenceActivite.session_id)
                .filter(PresenceActivite.participant_id == Participant.id)
                .filter(SessionActivite.secteur == active_secteur_filter)
                .exists()
            )
            participants_q = participants_q.filter(
                db.or_(
                    Participant.created_secteur == active_secteur_filter,
                    has_presence_in_user_secteur,
                )
            )
        rows = _run_ranked_rows(
            participants_q,
            [Participant.nom, Participant.prenom, Participant.email, Participant.telephone, Participant.ville, Participant.adresse, Participant.created_secteur, Quartier.nom, Quartier.ville],
            [Participant.updated_at.desc(), Participant.nom.asc(), Participant.prenom.asc()],
        )
        for row in rows:
            label = f"{(row.prenom or '').strip()} {(row.nom or '').strip()}".strip() or f"Participant #{row.id}"
            quartier_nom = (row.quartier.nom if row.quartier else "") or ""
            ville = (row.ville or (row.quartier.ville if row.quartier else "") or "").strip()
            meta_bits = [bit for bit in [quartier_nom, ville, row.email or row.telephone or "", row.created_secteur or ""] if bit]
            meta = " · ".join(meta_bits[:4]) or "Fiche participant"
            results.append({
                "type": "Participant",
                "label": label,
                "meta": meta,
                "secteur": row.created_secteur or "",
                "url": url_for("participants.edit_participant", participant_id=row.id),
                "score": _score_item(label, meta, row.adresse, quartier_nom, row.ville, row.email, row.telephone),
            })

    if (wanted_type in {None, "Quartier"}) and can("quartiers:view"):
        quartiers_q = Quartier.query
        rows = _run_ranked_rows(
            quartiers_q,
            [Quartier.nom, Quartier.ville, Quartier.description],
            [Quartier.ville.asc(), Quartier.nom.asc()],
        )
        for row in rows:
            if quartier_filter and quartier_filter not in _normalize_search_text(f"{row.nom} {row.ville} {row.description}"):
                continue
            label = row.nom
            meta_bits = [row.ville or "", "QPV" if row.is_qpv else "", row.description or ""]
            meta = " · ".join([bit for bit in meta_bits if bit][:3])
            results.append({
                "type": "Quartier",
                "label": label,
                "meta": meta,
                "secteur": "",
                "url": url_for("quartiers.edit", quartier_id=row.id),
                "score": _score_item(label, meta, row.description, row.ville),
            })

    if (wanted_type in {None, "Projet"}) and can("projets:view"):
        projets_q = Projet.query
        if active_secteur_filter:
            projets_q = projets_q.filter(Projet.secteur == active_secteur_filter)
        rows = _run_ranked_rows(
            projets_q,
            [Projet.nom, Projet.description, Projet.secteur],
            [Projet.created_at.desc(), Projet.nom.asc()],
        )
        for row in rows:
            label = row.nom
            meta = " · ".join([bit for bit in [row.secteur or "", (row.description or "")[:80].strip()] if bit][:2])
            results.append({
                "type": "Projet",
                "label": label,
                "meta": meta,
                "secteur": row.secteur or "",
                "url": url_for("projets.projets_edit", projet_id=row.id),
                "score": _score_item(label, meta, row.description, row.secteur),
            })

    if (wanted_type in {None, "Subvention"}) and can("subventions:view"):
        subventions_q = Subvention.query.filter(Subvention.est_archive.is_(False))
        if active_secteur_filter:
            subventions_q = subventions_q.filter(Subvention.secteur == active_secteur_filter)
        rows = _run_ranked_rows(
            subventions_q,
            [Subvention.nom, Subvention.secteur],
            [Subvention.annee_exercice.desc(), Subvention.created_at.desc(), Subvention.nom.asc()],
        )
        for row in rows:
            label = row.nom
            meta = " · ".join([bit for bit in [row.secteur or "", str(row.annee_exercice or "")] if bit])
            results.append({
                "type": "Subvention",
                "label": label,
                "meta": meta,
                "secteur": row.secteur or "",
                "url": url_for("main.subvention_pilotage", subvention_id=row.id),
                "score": _score_item(label, meta, row.secteur, str(row.annee_exercice or "")),
            })

    latest_session_subq = db.session.query(
        SessionActivite.atelier_id.label("atelier_id"),
        db.func.max(db.func.coalesce(SessionActivite.date_session, SessionActivite.rdv_date)).label("last_session_date"),
    ).group_by(SessionActivite.atelier_id).subquery()

    if (wanted_type in {None, "Atelier"}) and can("emargement:view"):
        ateliers_q = AtelierActivite.query.outerjoin(latest_session_subq, latest_session_subq.c.atelier_id == AtelierActivite.id).filter(AtelierActivite.is_deleted.is_(False))
        if active_secteur_filter:
            ateliers_q = ateliers_q.filter(AtelierActivite.secteur == active_secteur_filter)
        rows = _run_ranked_rows(
            ateliers_q,
            [AtelierActivite.nom, AtelierActivite.description, AtelierActivite.secteur, AtelierActivite.type_atelier],
            [latest_session_subq.c.last_session_date.desc().nullslast(), AtelierActivite.nom.asc()],
        )
        for row in rows:
            last_date = None
            try:
                last_date = max((s.date_session or s.rdv_date) for s in (row.sessions or []) if (s.date_session or s.rdv_date))
            except Exception:
                last_date = None
            meta_bits = [row.secteur or "", row.type_atelier or "", f"Dernière séance {last_date.strftime('%d/%m/%Y')}" if last_date else ""]
            label = row.nom
            meta = " · ".join([bit for bit in meta_bits if bit])
            results.append({
                "type": "Atelier",
                "label": label,
                "meta": meta,
                "secteur": row.secteur or "",
                "url": url_for("activite.sessions", atelier_id=row.id),
                "score": _score_item(label, meta, row.description, row.secteur, row.type_atelier),
            })

    if (wanted_type in {None, "Partenaire"}) and can("partenaires:view"):
        partenaires_q = Partenaire.query
        rows = _run_ranked_rows(
            partenaires_q,
            [Partenaire.nom, Partenaire.contact_nom, Partenaire.contact_prenom, Partenaire.email_contact, Partenaire.email_general, Partenaire.tel_contact, Partenaire.tel_general, Partenaire.adresse, Partenaire.description],
            [Partenaire.nom.asc()],
        )
        for row in rows:
            contact = " ".join([x for x in [row.contact_prenom, row.contact_nom] if x]).strip()
            meta_bits = [contact, row.email_contact or row.email_general or "", row.tel_contact or row.tel_general or "", row.adresse or ""]
            label = row.nom
            meta = " · ".join([bit for bit in meta_bits if bit][:4])
            results.append({
                "type": "Partenaire",
                "label": label,
                "meta": meta,
                "secteur": "",
                "url": url_for("partenaires.edit", partenaire_id=row.id),
                "score": _score_item(label, meta, row.description, row.contact_nom, row.contact_prenom, row.adresse),
            })

    results_sorted = sorted(
        results,
        key=lambda item: (
            -int(item.get("score") or 0),
            SEARCH_TYPE_PRIORITY.get(item.get("type") or "", 99),
            (item.get("label") or "").lower(),
        ),
    )
    type_facets = {}
    secteur_facets = {}
    for row in results_sorted:
        t = row.get("type") or "Autres"
        type_facets[t] = int(type_facets.get(t, 0)) + 1
        s = (row.get("secteur") or "").strip()
        if s:
            secteur_facets[s] = int(secteur_facets.get(s, 0)) + 1

    duration_ms = int((perf_counter() - start_ts) * 1000)
    current_app.logger.info(
        "global_search q=%r type=%r secteur=%r quartier=%r tokens=%s count=%s duration_ms=%s db=%s",
        term,
        wanted_type,
        active_secteur_filter,
        quartier_filter,
        tokens,
        min(len(results_sorted), panel_limit),
        duration_ms,
        dialect_name,
    )
    trimmed = [{k: v for k, v in row.items() if k != "score"} for row in results_sorted[:panel_limit]]
    full_rows = [{k: v for k, v in row.items() if k != "score"} for row in results_sorted[:page_limit]]
    return {
        "results": trimmed,
        "all_results": full_rows,
        "query": term,
        "debug": {"duration_ms": duration_ms},
        "facets": {"types": type_facets, "secteurs": secteur_facets},
        "meta": {
            "requested_type": wanted_type,
            "requested_secteur": active_secteur_filter,
            "requested_quartier": parsed["quartier_filter"] or "",
        },
    }

@bp.post("/ui-mode")
@login_required
def set_ui_mode():
    mode = (request.form.get("mode") or "simple").strip().lower()
    if mode not in {"simple", "expert"}:
        mode = "simple"
    session["ui_mode"] = mode
    try:
        save_dashboard_pref(current_user, ui_mode=mode, customized=True)
    except Exception:
        db.session.rollback()
    flash("Mode simplifié activé." if mode == "simple" else "Mode expert activé.", "success")
    next_url = (request.form.get("next") or request.referrer or url_for("main.dashboard")).strip()
    return redirect(next_url)


@bp.post("/ui-device-mode")
@login_required
def set_ui_device_mode():
    mode = (request.form.get("device_mode") or "desktop").strip().lower()
    if mode not in {"desktop", "mobile", "tablet", "kiosk"}:
        mode = "desktop"
    session["ui_device_mode"] = mode
    flash(f"Mode d’écran activé : {mode}.", "success")
    next_url = (request.form.get("next") or request.referrer or url_for("main.dashboard")).strip()
    resp = redirect(next_url)
    resp.set_cookie("ui_device_mode", mode, max_age=60 * 60 * 24 * 365, samesite="Lax")
    return resp



@bp.route("/dashboard/personnaliser", methods=["GET", "POST"])
@login_required
@require_perm("dashboard:view")
def dashboard_customize():
    if request.method == "POST":
        quick_actions = []
        for idx in range(1, 7):
            key = (request.form.get(f"quick_action_{idx}") or "").strip()
            if key and key not in quick_actions:
                quick_actions.append(key)

        widgets = []
        for key in ["alerts", "charts", "recents"]:
            try:
                position = int(request.form.get(f"widget_{key}_position") or 99)
            except Exception:
                position = 99
            widgets.append({
                "key": key,
                "visible": request.form.get(f"widget_{key}_visible") == "1",
                "position": position,
            })

        try:
            save_dashboard_pref(
                current_user,
                quick_actions=quick_actions,
                widgets=widgets,
                ui_mode=(request.form.get("ui_mode") or None),
                customized=True,
            )
            session["ui_mode"] = (request.form.get("ui_mode") or session.get("ui_mode") or "simple").strip().lower()
            flash("L’accueil a bien été personnalisé.", "success")
        except Exception:
            db.session.rollback()
            flash("Impossible d’enregistrer la personnalisation de l’accueil.", "danger")
        return redirect(url_for("main.dashboard_customize"))

    prefs = load_dashboard_pref(current_user)
    quick_actions_catalog = available_quick_actions(current_user)
    widgets_catalog = available_widgets()
    widget_prefs = {item["key"]: item for item in prefs["widgets"]}
    quick_slots = prefs["quick_actions"][:6]
    while len(quick_slots) < 6:
        quick_slots.append("")
    return render_template(
        "dashboard_customize.html",
        prefs=prefs,
        quick_actions_catalog=quick_actions_catalog,
        widgets_catalog=widgets_catalog,
        widget_prefs=widget_prefs,
        quick_slots=quick_slots,
    )


@bp.post("/dashboard/reinitialiser")
@login_required
@require_perm("dashboard:view")
def dashboard_reset():
    try:
        prefs = reset_dashboard_pref(current_user)
        session["ui_mode"] = prefs.get("ui_mode") or "simple"
        flash("L’accueil par défaut a bien été rétabli.", "success")
    except Exception:
        db.session.rollback()
        flash("Impossible de réinitialiser l’accueil.", "danger")
    return redirect(request.form.get("next") or url_for("main.dashboard"))


# --------- Permissions ---------
def can_see_secteur(secteur: str) -> bool:
    return can_access_secteur(secteur)


def _parse_money(value, default=0.0) -> float:
    raw = str(value or "").replace(" ", "").replace(",", ".")
    try:
        return float(raw) if raw else float(default)
    except Exception:
        return float(default)


def _ref_scope_query(query, model, secteur: str | None):
    if secteur:
        return query.filter((model.secteur.is_(None)) | (model.secteur == secteur))
    return query


def _budget_categories_ref_for_secteur(secteur: str | None = None, nature: str | None = None, active_only: bool = True):
    q = BudgetCategorieReferentiel.query.join(BudgetCompteReferentiel)
    q = _ref_scope_query(q, BudgetCategorieReferentiel, secteur)
    if secteur:
        q = q.filter((BudgetCompteReferentiel.secteur.is_(None)) | (BudgetCompteReferentiel.secteur == secteur))
    if nature in ("charge", "produit"):
        q = q.filter(BudgetCategorieReferentiel.nature == nature)
    if active_only:
        q = q.filter(BudgetCategorieReferentiel.actif.is_(True), BudgetCompteReferentiel.actif.is_(True))
    return q.order_by(
        BudgetCompteReferentiel.nature.asc(),
        BudgetCompteReferentiel.ordre.asc(),
        BudgetCompteReferentiel.code.asc(),
        BudgetCategorieReferentiel.ordre.asc(),
        BudgetCategorieReferentiel.libelle.asc(),
    ).all()


def _budget_category_allowed(cat: BudgetCategorieReferentiel, secteur: str | None, nature: str | None = None) -> bool:
    if not cat or not getattr(cat, "compte", None):
        return False
    if nature in ("charge", "produit") and cat.nature != nature:
        return False
    if cat.secteur and secteur and cat.secteur != secteur:
        return False
    if cat.compte.secteur and secteur and cat.compte.secteur != secteur:
        return False
    return bool(cat.actif and cat.compte.actif)


def _budget_category_compte_label(cat: BudgetCategorieReferentiel) -> str:
    if not cat or not getattr(cat, "compte", None):
        return ""
    return f"{cat.compte.code} - {cat.compte.libelle}".strip(" -")


def _compute_prorata(lignes, montant_cible: float):
    """
    Calcule une répartition pro-rata sur montant_base.
    Ne modifie pas la DB : retourne un dict {ligne_id: montant_theorique}
    Ajuste la dernière ligne pour tomber pile au centime.
    """
    lignes = list(lignes)
    out = {}
    if not lignes:
        return out

    total_base = sum(float(l.montant_base or 0) for l in lignes)
    if total_base <= 0:
        for l in lignes:
            out[l.id] = 0.0
        return out

    ratio = float(montant_cible or 0) / total_base

    cumul = 0.0
    for i, l in enumerate(lignes):
        base = float(l.montant_base or 0)
        part = round(base * ratio, 2)
        if i == len(lignes) - 1:
            part = round(float(montant_cible or 0) - cumul, 2)
        out[l.id] = float(part)
        cumul += float(part)

    return out



def _auto_fit_worksheet(ws, min_width: int = 10, max_width: int = 42):
    for col_cells in ws.columns:
        try:
            idx = col_cells[0].column
        except Exception:
            continue
        max_len = 0
        for cell in col_cells:
            val = "" if cell.value is None else str(cell.value)
            max_len = max(max_len, len(val))
        ws.column_dimensions[get_column_letter(idx)].width = max(min_width, min(max_len + 2, max_width))


def _write_table(ws, title: str, headers: list[str], rows: list[list], *, start_row: int = 1) -> int:
    row = start_row
    ws.cell(row=row, column=1, value=title)
    ws.cell(row=row, column=1).font = Font(bold=True, size=12)
    row += 1
    fill = PatternFill(fill_type="solid", fgColor="DCE6F1")
    for idx, header in enumerate(headers, start=1):
        c = ws.cell(row=row, column=idx, value=header)
        c.font = Font(bold=True)
        c.fill = fill
    row += 1
    for data in rows:
        for idx, value in enumerate(data, start=1):
            ws.cell(row=row, column=idx, value=value)
        row += 1
    return row


def _compute_bilan_global_payload():
    has_global_scope = can("scope:all_secteurs")
    annee_raw = (request.args.get("annee") or "").strip()
    secteur_raw = (request.args.get("secteur") or "").strip()
    projet_id_raw = (request.args.get("projet_id") or "").strip()

    selected_annee = None
    if annee_raw:
        try:
            selected_annee = int(annee_raw)
        except ValueError:
            selected_annee = None

    selected_secteur = secteur_raw or None
    selected_projet_id = None
    if projet_id_raw:
        try:
            selected_projet_id = int(projet_id_raw)
        except ValueError:
            selected_projet_id = None

    if not has_global_scope:
        selected_secteur = current_user.secteur_assigne
        if selected_projet_id:
            pjt = Projet.query.get(selected_projet_id)
            sec_pjt = (pjt.secteur or "").strip().lower() if pjt else ""
            sec_user = (selected_secteur or "").strip().lower()
            if (not pjt) or (sec_pjt != sec_user):
                selected_projet_id = None

    q = Subvention.query.filter_by(est_archive=False)
    if selected_annee is not None:
        q = q.filter(Subvention.annee_exercice == selected_annee)
    if selected_secteur:
        q = q.filter(Subvention.secteur == selected_secteur)
    if selected_projet_id:
        q = q.join(SubventionProjet, SubventionProjet.subvention_id == Subvention.id).filter(SubventionProjet.projet_id == selected_projet_id)

    subs = q.order_by(Subvention.annee_exercice.desc(), Subvention.secteur.asc(), Subvention.nom.asc()).all()

    totals = {
        "demande": round(sum(float(s.montant_demande or 0) for s in subs), 2),
        "attribue": round(sum(float(s.montant_attribue or 0) for s in subs), 2),
        "recu": round(sum(float(s.montant_recu or 0) for s in subs), 2),
        "reel_lignes": round(sum(float(s.total_reel_lignes or 0) for s in subs), 2),
        "engage": round(sum(float(s.total_engage or 0) for s in subs), 2),
        "reste": round(sum(float(s.total_reste or 0) for s in subs), 2),
    }

    alertes = []
    for s in subs:
        recu = float(s.montant_recu or 0)
        reel_lignes = float(s.total_reel_lignes or 0)
        engage = float(s.total_engage or 0)
        if recu > 0 and reel_lignes == 0:
            alertes.append(f"{s.nom} : reçu {recu:.2f}€ mais lignes réel = 0€ (ventilation manquante).")
        if recu > 0 and reel_lignes > 0 and reel_lignes < recu:
            alertes.append(f"{s.nom} : reçu {recu:.2f}€ mais lignes réel = {reel_lignes:.2f}€ (ventilation incomplète).")
        if reel_lignes > 0 and engage > reel_lignes:
            alertes.append(f"{s.nom} : engagé {engage:.2f}€ > lignes réel {reel_lignes:.2f}€ (dépassement).")

    secteurs = current_app.config.get("SECTEURS", [])
    if not secteurs:
        secteurs = [r[0] for r in db.session.query(db.distinct(Subvention.secteur)).all() if r[0]]
    if not has_global_scope:
        secteurs = [current_user.secteur_assigne]

    projets_q = Projet.query
    if not has_global_scope:
        projets_q = projets_q.filter(Projet.secteur == current_user.secteur_assigne)
    projets = projets_q.order_by(Projet.secteur.asc(), Projet.nom.asc()).all()

    return {
        "subs": subs,
        "totals_dict": totals,
        "totals": type("Obj", (), totals),
        "alertes": alertes,
        "secteurs": secteurs,
        "projets": projets,
        "selected_annee": selected_annee,
        "selected_secteur": selected_secteur,
        "selected_projet_id": selected_projet_id,
    }


def _build_bilan_global_workbook(payload: dict):
    subs = payload["subs"]
    totals = payload["totals_dict"]
    selected_annee = payload["selected_annee"]
    selected_secteur = payload["selected_secteur"]
    selected_projet_id = payload["selected_projet_id"]
    projets = payload["projets"]
    alertes = payload["alertes"]

    projet_label = "Tous"
    if selected_projet_id:
        p = next((x for x in projets if x.id == selected_projet_id), None)
        if p:
            projet_label = f"{p.secteur} · {p.nom}"

    wb = Workbook()
    ws_params = wb.active
    ws_params.title = "Paramètres"
    _write_table(ws_params, "Périmètre exact de l'export", ["Paramètre", "Valeur"], [
        ["Année", selected_annee or "Toutes"],
        ["Secteur", selected_secteur or "Tous"],
        ["Projet", projet_label],
        ["Date d'export", date.today().isoformat()],
        ["Utilisateur", getattr(current_user, "email", None) or getattr(current_user, "username", None) or f"user#{getattr(current_user, 'id', '')}"],
        ["Subventions incluses", len(subs)],
    ], start_row=1)

    ws_syn = wb.create_sheet("Synthèse")
    _write_table(ws_syn, "Synthèse financière", ["Indicateur", "Valeur €"], [
        ["Demandé", totals.get("demande", 0)],
        ["Attribué", totals.get("attribue", 0)],
        ["Reçu", totals.get("recu", 0)],
        ["Ventilé réel", totals.get("reel_lignes", 0)],
        ["Engagé", totals.get("engage", 0)],
        ["Reste", totals.get("reste", 0)],
    ], start_row=1)

    ws_subs = wb.create_sheet("Subventions")
    _write_table(ws_subs, "Subventions incluses", ["Année", "Secteur", "Subvention", "Demandé €", "Attribué €", "Reçu €", "Ventilé réel €", "Engagé €", "Reste €"], [
        [s.annee_exercice, s.secteur, s.nom, float(s.montant_demande or 0), float(s.montant_attribue or 0), float(s.montant_recu or 0), float(s.total_reel_lignes or 0), float(s.total_engage or 0), float(s.total_reste or 0)]
        for s in subs
    ], start_row=1)

    ws_alert = wb.create_sheet("Alertes")
    _write_table(ws_alert, "Alertes", ["Message"], [[a] for a in alertes] or [["Aucune alerte"]], start_row=1)

    for ws in wb.worksheets:
        _auto_fit_worksheet(ws)
    return wb


# --------- Setup start ---------


# ---------------------------------------------------------------------
# P0.3C — Hubs métier
# ---------------------------------------------------------------------

def _hub_forbidden_if_empty(cards):
    if not cards:
        abort(403)


@bp.route("/publics")
@login_required
def hub_publics():
    cards = []

    if can("participants:view") or can("participants:view_all"):
        cards.append({
            "title": "Participants",
            "subtitle": "Retrouver, créer ou mettre à jour une fiche habitant.",
            "primary_label": "Ouvrir les participants",
            "primary_url": url_for("participants.list_participants"),
            "secondary": [
                {"label": "Ajouter une personne", "url": url_for("participants.new_participant")} if can("participants:edit") else None,
                {"label": "Doublons potentiels", "url": url_for("participants.duplicates")} if can("participants:edit") else None,
            ],
            "tag": "Publics",
        })

    if can("insertion:view"):
        cards.append({
            "title": "Insertion",
            "subtitle": "Suivre les parcours, positionnements et données insertion.",
            "primary_label": "Ouvrir insertion",
            "primary_url": url_for("insertion.index"),
            "secondary": [],
            "tag": "Parcours",
        })

    if can("quartiers:view"):
        cards.append({
            "title": "Quartiers",
            "subtitle": "Consulter les quartiers, QPV et informations territoriales.",
            "primary_label": "Ouvrir quartiers",
            "primary_url": url_for("quartiers.index"),
            "secondary": [],
            "tag": "Territoire",
        })

    _hub_forbidden_if_empty(cards)
    return render_template(
        "hub_publics.html",
        title="Publics & parcours",
        intro="Une porte d’entrée pour tout ce qui concerne les habitants, leurs parcours et leur territoire.",
        cards=cards,
    )


@bp.route("/activites")
@login_required
def hub_activites():
    cards = []

    if can("emargement:view"):
        cards.append({
            "title": "Présences / émargement",
            "subtitle": "Faire l’émargement, ouvrir les ateliers et gérer les sessions.",
            "primary_label": "Ouvrir les présences",
            "primary_url": url_for("activite.index"),
            "secondary": [
                {"label": "Modèles d’émargement", "url": url_for("activite.emargement_models")} if can("emargement:edit") else None,
            ],
            "tag": "Quotidien",
        })

    if can("statsimpact:view") or can("stats:view"):
        cards.append({
            "title": "Données ateliers",
            "subtitle": "Suivre les statistiques d’activité, présences et ateliers.",
            "primary_label": "Voir les données",
            "primary_url": url_for("statsimpact.dashboard"),
            "secondary": [],
            "tag": "Analyse",
        })

    if can("pedagogie:view"):
        cards.append({
            "title": "Pédagogie",
            "subtitle": "Référentiels, compétences, modules et suivi pédagogique.",
            "primary_label": "Ouvrir pédagogie",
            "primary_url": url_for("pedagogie.referentiels_list"),
            "secondary": [
                {"label": "Suivi pédagogique", "url": url_for("pedagogie.suivi_pedagogique")},
            ],
            "tag": "Compétences",
        })

    _hub_forbidden_if_empty(cards)
    return render_template(
        "hub_activites.html",
        title="Activités & présences",
        intro="Un hub pour passer des séances aux présences, puis aux données d’activité et au suivi pédagogique.",
        cards=cards,
    )


@bp.route("/bilans-hub")
@login_required
def hub_bilans():
    cards = []

    if can("stats:view"):
        cards.append({
            "title": "Stats & bilans",
            "subtitle": "Consulter les chiffres clés et les indicateurs de pilotage.",
            "primary_label": "Ouvrir stats & bilans",
            "primary_url": url_for("main.stats_bilans"),
            "secondary": [
                {"label": "Bilan global", "url": url_for("main.bilan_global")},
                {"label": "Export bilan XLSX", "url": url_for("main.bilan_global_export_xlsx")},
            ],
            "tag": "Pilotage",
        })

    if can("bilans:view"):
        cards.append({
            "title": "Bilans lourds",
            "subtitle": "Préparer les bilans annuels, narratifs et exports complets.",
            "primary_label": "Ouvrir bilans lourds",
            "primary_url": url_for("bilans.bilans_lourds", year=date.today().year),
            "secondary": [
                {"label": "Bilan secteur", "url": url_for("bilans.bilan_secteur")},
                {"label": "Bilan subvention", "url": url_for("bilans.bilan_subvention")},
                {"label": "Qualité des données", "url": url_for("bilans.qualite")},
            ],
            "tag": "Annuel",
        })

    if can("questionnaires:view"):
        cards.append({
            "title": "Questionnaires d’impact",
            "subtitle": "Consulter les questionnaires et retours qualitatifs.",
            "primary_label": "Ouvrir questionnaires",
            "primary_url": url_for("questionnaires.index"),
            "secondary": [],
            "tag": "Impact",
        })

    _hub_forbidden_if_empty(cards)
    return render_template(
        "hub_bilans.html",
        title="Bilans & exports",
        intro="La zone pour préparer les bilans, vérifier les données et sortir les exports utiles.",
        cards=cards,
    )


@bp.route("/ressources")
@login_required
def hub_ressources():
    cards = []

    if can("inventaire:view"):
        cards.append({
            "title": "Inventaire matériel",
            "subtitle": "Suivre le matériel, les achats et les équipements liés aux dépenses.",
            "primary_label": "Ouvrir inventaire",
            "primary_url": url_for("inventaire_materiel.list_items"),
            "secondary": [
                {"label": "Ajouter du matériel", "url": url_for("inventaire_materiel.new_item")} if can("inventaire:edit") else None,
            ],
            "tag": "Matériel",
        })

    if can("partenaires:view"):
        cards.append({
            "title": "Annuaire partenaires",
            "subtitle": "Retrouver les structures, contacts et interventions partenaires.",
            "primary_label": "Ouvrir partenaires",
            "primary_url": url_for("partenaires.index"),
            "secondary": [
                {"label": "Ajouter un partenaire", "url": url_for("partenaires.create")} if can("partenaires:edit") else None,
            ],
            "tag": "Réseau",
        })

    _hub_forbidden_if_empty(cards)
    return render_template(
        "hub_ressources.html",
        title="Ressources",
        intro="Les ressources utiles autour des projets : matériel, partenaires et outils de soutien.",
        cards=cards,
    )




# ---------------------------------------------------------------------
# P0.3F — Audit navigation / templates
# ---------------------------------------------------------------------

def _p03f_collect_endpoints():
    try:
        return set(current_app.view_functions.keys())
    except Exception:
        return set()


def _p03f_scan_templates():
    templates_dir = Path(current_app.root_path) / "templates"
    endpoints = _p03f_collect_endpoints()
    rows = []

    if not templates_dir.exists():
        return [{
            "level": "danger",
            "file": "app/templates",
            "type": "templates",
            "message": "Dossier templates introuvable.",
            "detail": str(templates_dir),
        }]

    # Ne pas confondre safe_url_for(...) avec url_for(...).
    url_for_re = re.compile(r"(?<!safe_)url_for\(\s*['\"]([^'\"]+)['\"]")
    endpoint_re = re.compile(r"request\.endpoint\s*==\s*['\"]([^'\"]+)['\"]")
    has_perm_re = re.compile(r"\bhas_perm\s*\(")

    for path in sorted(templates_dir.rglob("*.html")):
        rel = path.relative_to(current_app.root_path).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="latin-1", errors="ignore")

        for endpoint in url_for_re.findall(text):
            if endpoint not in endpoints:
                rows.append({
                    "level": "danger",
                    "file": rel,
                    "type": "url_for",
                    "message": f"Endpoint introuvable : {endpoint}",
                    "detail": "Corriger le nom d’endpoint ou supprimer le lien.",
                })

        for endpoint in endpoint_re.findall(text):
            if endpoint not in endpoints:
                rows.append({
                    "level": "warning",
                    "file": rel,
                    "type": "request.endpoint",
                    "message": f"Comparaison avec endpoint inexistant : {endpoint}",
                    "detail": "Peut simplement empêcher le bon état actif du menu.",
                })

        if has_perm_re.search(text):
            rows.append({
                "level": "danger",
                "file": rel,
                "type": "has_perm",
                "message": "Usage de has_perm(...) dans un template.",
                "detail": "Utiliser can(...) dans les templates.",
            })

    if not rows:
        rows.append({
            "level": "ok",
            "file": "templates",
            "type": "audit",
            "message": "Aucun problème évident détecté dans les templates.",
            "detail": "",
        })

    return rows


def _p03f_code_without_comments(text: str) -> str:
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        lines.append(line)
    return "\n".join(lines)


def _p03f_has_unguarded_sqlite_strftime(text: str) -> bool:
    clean = _p03f_code_without_comments(text)
    needle = "func." + "strftime"
    if needle not in clean:
        return False

    # Cas admis : fonction helper qui choisit explicitement SQLite vs PostgreSQL.
    lowered = clean.lower()
    if "_dialect_name" in clean and "sqlite" in lowered and ("date_trunc" in lowered or "to_char" in lowered):
        return False

    return True


def _p03f_scan_python_routes():
    app_dir = Path(current_app.root_path)
    endpoints = _p03f_collect_endpoints()
    rows = []
    url_for_re = re.compile(r"(?<!safe_)url_for\(\s*['\"]([^'\"]+)['\"]")

    ignored_suffixes = (" - Copie.py", ".bak", ".old", ".tmp")

    for path in sorted(app_dir.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        if path.name.endswith(ignored_suffixes):
            continue

        rel = path.relative_to(app_dir.parent).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="latin-1", errors="ignore")

        for endpoint in url_for_re.findall(text):
            if endpoint not in endpoints:
                rows.append({
                    "level": "warning",
                    "file": rel,
                    "type": "url_for python",
                    "message": f"Endpoint potentiellement introuvable : {endpoint}",
                    "detail": "À vérifier : certains endpoints peuvent être conditionnels ou rarement utilisés.",
                })

        if _p03f_has_unguarded_sqlite_strftime(text):
            rows.append({
                "level": "danger",
                "file": rel,
                "type": "postgres",
                "message": "Usage SQL strftime non protégé détecté.",
                "detail": "Remplacer par extract(...) ou prévoir un branchement SQLite/PostgreSQL.",
            })

    if not rows:
        rows.append({
            "level": "ok",
            "file": "app",
            "type": "audit",
            "message": "Aucun problème évident détecté dans les routes Python.",
            "detail": "",
        })

    return rows



@bp.route("/controle/navigation")
@login_required
@require_perm("controle:view")
def controle_navigation():
    template_rows = _p03f_scan_templates()
    python_rows = _p03f_scan_python_routes()
    all_rows = template_rows + python_rows

    summary = {
        "danger": sum(1 for r in all_rows if r.get("level") == "danger"),
        "warning": sum(1 for r in all_rows if r.get("level") == "warning"),
        "ok": sum(1 for r in all_rows if r.get("level") == "ok"),
        "total": len(all_rows),
    }

    return render_template(
        "controle_navigation.html",
        summary=summary,
        template_rows=template_rows,
        python_rows=python_rows,
    )


@bp.route("/setup-start")
def setup_start():
    # simple page de diagnostic / aide
    return render_template("controle.html")


# --------- Dashboard ---------
@bp.route("/dashboard")
@login_required
@require_perm("dashboard:view")
def dashboard():
    raw_period = (request.args.get("period") or "").strip().lower()
    try:
        days = int(request.args.get("days") or 90)
    except Exception:
        days = 90
    if raw_period in {"30", "90", "365"}:
        try:
            days = int(raw_period)
        except Exception:
            days = 90
    try:
        budget_year = int(request.args.get("budget_year") or date.today().year)
    except Exception:
        budget_year = date.today().year

    ctx = build_dashboard_context(
        current_user,
        days=days,
        budget_year=budget_year,
        period_key=raw_period or str(days),
    )
    prefs = load_dashboard_pref(current_user)
    ctx["dashboard_prefs"] = prefs
    ctx["dashboard_widgets"] = prefs.get("widgets") or []
    return render_template("dashboard.html", **ctx)


# --------- List subventions ---------
@bp.route("/subventions")
@login_required
@require_perm("subventions:view")
def subventions_list():
    secteurs = current_app.config.get("SECTEURS", [])

    base_q = Subvention.query.filter_by(est_archive=False)
    if not can("scope:all_secteurs"):
        base_q = base_q.filter(Subvention.secteur == current_user.secteur_assigne)

    years = [
        y for (y,) in base_q.with_entities(Subvention.annee_exercice).distinct().order_by(Subvention.annee_exercice.desc()).all()
        if y is not None
    ]
    try:
        selected_year = int(request.args.get("annee") or (years[0] if years else date.today().year))
    except Exception:
        selected_year = years[0] if years else date.today().year

    subs_q = base_q.filter(Subvention.annee_exercice == selected_year)
    subs = subs_q.order_by(Subvention.annee_exercice.desc(), Subvention.nom.asc()).all()

    default_secteur = current_user.secteur_assigne if not can("scope:all_secteurs") else (secteurs[0] if secteurs else None)
    categories_ref = _budget_categories_ref_for_secteur(default_secteur)
    return render_template(
        "subventions_list.html",
        subs=subs,
        secteurs=secteurs,
        selected_year=selected_year,
        available_years=years,
        categories_ref=categories_ref,
    )


@bp.route("/subvention/nouvelle", methods=["POST"])
@login_required
@require_perm('subventions:edit')
def subvention_create():
    nom = (request.form.get("nom") or "").strip()
    secteur = (request.form.get("secteur") or "").strip()
    annee = int(request.form.get("annee_exercice") or 2025)

    montant_demande = float(request.form.get("montant_demande") or 0)
    montant_attribue = float(request.form.get("montant_attribue") or 0)
    montant_recu = float(request.form.get("montant_recu") or 0)

    if not can("scope:all_secteurs"):
        secteur = current_user.secteur_assigne

    if not nom or not secteur:
        flash("Nom + secteur obligatoires.", "danger")
        return redirect(url_for("main.subventions_list"))

    if not can_see_secteur(secteur):
        abort(403)

    s = Subvention(
        nom=nom,
        secteur=secteur,
        annee_exercice=annee,
        montant_demande=montant_demande,
        montant_attribue=montant_attribue,
        montant_recu=montant_recu,
    )
    db.session.add(s)
    db.session.flush()

    selected_cat_ids = [int(x) for x in request.form.getlist("categorie_ref_id") if str(x).isdigit()]
    if selected_cat_ids:
        cats = BudgetCategorieReferentiel.query.filter(BudgetCategorieReferentiel.id.in_(selected_cat_ids)).all()
        for cat in cats:
            if not _budget_category_allowed(cat, secteur):
                continue
            db.session.add(LigneBudget(
                subvention_id=s.id,
                nature=cat.nature,
                compte=_budget_category_compte_label(cat) or ("74" if cat.nature == "produit" else "60"),
                libelle=cat.libelle,
                montant_base=float(cat.montant_defaut or 0.0),
                montant_reel=0.0,
            ))

    db.session.commit()

    flash("Subvention créée.", "success")
    return redirect(url_for("main.subvention_pilotage", subvention_id=s.id))


# --------- Pilotage subvention ---------
@bp.route("/subvention/<int:subvention_id>/pilotage", methods=["GET", "POST"])
@login_required
@require_perm("subventions:view")
def subvention_pilotage(subvention_id):
    sub = Subvention.query.get_or_404(subvention_id)
    if not can_see_secteur(sub.secteur):
        abort(403)

    if request.method == "POST":
        if not can("subventions:edit"):
            abort(403)
        action = request.form.get("action") or ""

        # --- Montants globaux ---
        if action == "update_montants":
            sub.montant_demande = float(request.form.get("montant_demande") or 0)
            sub.montant_attribue = float(request.form.get("montant_attribue") or 0)
            sub.montant_recu = float(request.form.get("montant_recu") or 0)
            db.session.commit()
            flash("Montants mis à jour.", "success")
            return redirect(url_for("main.subvention_pilotage", subvention_id=sub.id))

        # --- Ajouter une ligne ---
        if action == "add_ligne":
            nature = (request.form.get("nature") or "charge").strip()
            cat_id = int(request.form.get("categorie_ref_id") or 0)
            cat = None
            if cat_id:
                cat = BudgetCategorieReferentiel.query.get_or_404(cat_id)
                if not _budget_category_allowed(cat, sub.secteur):
                    abort(400)
                nature = cat.nature

            compte_default = _budget_category_compte_label(cat) if cat else ("74" if nature == "produit" else "60")
            libelle_default = cat.libelle if cat else ""
            montant_default = float(cat.montant_defaut or 0.0) if cat else 0.0

            compte = (request.form.get("compte") or compte_default).strip()
            libelle = (request.form.get("libelle") or libelle_default).strip()
            montant_base = _parse_money(request.form.get("montant_base"), montant_default)
            montant_reel = _parse_money(request.form.get("montant_reel"), 0.0)

            if not libelle:
                flash("Libellé obligatoire.", "danger")
                return redirect(url_for("main.subvention_pilotage", subvention_id=sub.id))

            l = LigneBudget(
                subvention_id=sub.id,
                nature=nature,
                compte=compte,
                libelle=libelle,
                montant_base=montant_base,
                montant_reel=montant_reel,
            )
            db.session.add(l)
            db.session.commit()
            flash("Ligne ajoutée.", "success")
            return redirect(url_for("main.subvention_pilotage", subvention_id=sub.id))

        # --- Ventilation automatique (écrit dans montant_reel) ---
        if action == "auto_ventilation":
            mode = (request.form.get("mode") or "copy_base").strip()
            target = (request.form.get("target") or "recu").strip()

            if target == "attribue":
                montant_cible = float(sub.montant_attribue or 0)
            else:
                montant_cible = float(sub.montant_recu or 0)

            lignes = list(sub.lignes)
            if not lignes:
                flash("Aucune ligne à ventiler.", "warning")
                return redirect(url_for("main.subvention_pilotage", subvention_id=sub.id))

            if mode == "reset":
                for l in lignes:
                    l.montant_reel = 0.0
                db.session.commit()
                flash("Ventilation réinitialisée (réel = 0).", "warning")
                return redirect(url_for("main.subvention_pilotage", subvention_id=sub.id))

            if mode == "copy_base":
                for l in lignes:
                    l.montant_reel = float(l.montant_base or 0)
                db.session.commit()
                flash("Ventilation : base copiée vers réel.", "success")
                return redirect(url_for("main.subvention_pilotage", subvention_id=sub.id))

            if mode == "prorata_base":
                total_base = sum(float(l.montant_base or 0) for l in lignes)
                if total_base <= 0:
                    flash("Impossible : total des bases = 0.", "danger")
                    return redirect(url_for("main.subvention_pilotage", subvention_id=sub.id))

                theor = _compute_prorata(lignes, montant_cible)
                for l in lignes:
                    l.montant_reel = float(theor.get(l.id, 0.0))
                db.session.commit()
                flash(f"Ventilation pro-rata effectuée sur {montant_cible:.2f}€.", "success")
                return redirect(url_for("main.subvention_pilotage", subvention_id=sub.id))

            abort(400)

        abort(400)

    # --- GET : données pour page ---
    projets_q = Projet.query.filter(Projet.secteur == sub.secteur)
    if not can("scope:all_secteurs"):
        projets_q = projets_q.filter(Projet.secteur == current_user.secteur_assigne)

    projets = projets_q.order_by(Projet.nom.asc()).all()
    linked_ids = set(sp.projet_id for sp in sub.projets)

    lignes = list(sub.lignes)
    total_base = round(sum(float(l.montant_base or 0) for l in lignes), 2)

    theor_recu = _compute_prorata(lignes, float(sub.montant_recu or 0))
    theor_attribue = _compute_prorata(lignes, float(sub.montant_attribue or 0))

    recu = float(sub.montant_recu or 0)
    reel_lignes = float(sub.total_reel_lignes or 0)
    engage = float(sub.total_engage or 0)

    warnings = []
    if recu > 0 and reel_lignes == 0:
        warnings.append("Tu as un montant reçu, mais aucune ventilation en lignes réel : utilise la ventilation auto ou renseigne le réel par ligne.")
    if recu > 0 and reel_lignes > 0 and reel_lignes < recu:
        warnings.append("Ventilation partielle : total lignes réel < montant reçu. Il manque une répartition.")
    if reel_lignes > 0 and engage > reel_lignes:
        warnings.append("Attention : engagé > total lignes réel (dépenses au-dessus de l'enveloppe ventilée).")

    return render_template(
        "budget_pilotage.html",
        sub=sub,
        projets=projets,
        linked_ids=linked_ids,
        total_base=total_base,
        theor_recu=theor_recu,
        theor_attribue=theor_attribue,
        warnings=warnings,
        categories_ref=_budget_categories_ref_for_secteur(sub.secteur),
    )


@bp.route("/subvention/<int:subvention_id>/delete", methods=["POST"])
@login_required
@require_perm('subventions:delete')
def subvention_delete(subvention_id):
    sub = Subvention.query.get_or_404(subvention_id)
    if not can_see_secteur(sub.secteur):
        abort(403)

    db.session.delete(sub)
    commit_delete(
        f"la subvention « {sub.nom} »",
        "Subvention supprimée.",
        success_category="warning",
        blocked_message=f"Impossible de supprimer la subvention « {sub.nom} » : elle est encore liée à d'autres données.",
    )
    return redirect(url_for("main.subventions_list"))


# --------- Edit / Delete lignes ---------
@bp.route("/ligne/<int:ligne_id>/edit", methods=["POST"])
@login_required
@require_perm("subventions:edit")
def ligne_edit(ligne_id):
    l = LigneBudget.query.get_or_404(ligne_id)
    sub = l.source_sub
    if not can_see_secteur(sub.secteur):
        abort(403)

    cat_id = int(request.form.get("categorie_ref_id") or 0)
    cat = None
    if cat_id:
        cat = BudgetCategorieReferentiel.query.get_or_404(cat_id)
        if not _budget_category_allowed(cat, sub.secteur):
            abort(400)

    l.nature = (request.form.get("nature") or (cat.nature if cat else getattr(l, "nature", "charge"))).strip()
    l.compte = (request.form.get("compte") or (_budget_category_compte_label(cat) if cat else l.compte)).strip()
    l.libelle = (request.form.get("libelle") or (cat.libelle if cat else l.libelle)).strip()
    l.montant_base = _parse_money(request.form.get("montant_base"), l.montant_base or 0)
    l.montant_reel = _parse_money(request.form.get("montant_reel"), l.montant_reel or 0)
    db.session.commit()

    flash("Ligne modifiée.", "success")
    return redirect(url_for("main.subvention_pilotage", subvention_id=sub.id))


@bp.route("/ligne/<int:ligne_id>/delete", methods=["POST"])
@login_required
@require_perm('budget:delete')
def ligne_delete(ligne_id):
    l = LigneBudget.query.get_or_404(ligne_id)
    sub = l.source_sub
    if not can_see_secteur(sub.secteur):
        abort(403)

    db.session.delete(l)
    commit_delete(
        f"la ligne « {l.libelle} »",
        "Ligne supprimée.",
        success_category="warning",
        blocked_message=f"Impossible de supprimer la ligne « {l.libelle} » : elle est encore utilisée ailleurs.",
    )
    return redirect(url_for("main.subvention_pilotage", subvention_id=sub.id))


# --------- Lier / délier subvention à projet ---------
@bp.route("/subvention/<int:subvention_id>/toggle_projet", methods=["POST"])
@login_required
@require_perm("subventions:link")
def subvention_toggle_projet(subvention_id):
    sub = Subvention.query.get_or_404(subvention_id)
    if not can_see_secteur(sub.secteur):
        abort(403)

    projet_id = int(request.form.get("projet_id") or 0)
    projet = Projet.query.get_or_404(projet_id)

    if projet.secteur != sub.secteur:
        abort(400)

    link = SubventionProjet.query.filter_by(projet_id=projet.id, subvention_id=sub.id).first()
    if link:
        db.session.delete(link)
        db.session.commit()
        flash("Subvention retirée du projet.", "warning")
    else:
        link = SubventionProjet(projet_id=projet.id, subvention_id=sub.id)
        db.session.add(link)
        db.session.commit()
        flash("Subvention ajoutée au projet.", "success")

    return redirect(url_for("main.subvention_pilotage", subvention_id=sub.id))


# --------- APIs pour dropdowns dépenses ---------
@bp.route("/api/subvention/<int:subvention_id>/comptes")
@login_required
@require_perm("subventions:view")
def api_comptes(subvention_id):
    sub = Subvention.query.get_or_404(subvention_id)
    if not can_see_secteur(sub.secteur):
        abort(403)

    nature = request.args.get("nature")

    q = LigneBudget.query.filter_by(subvention_id=sub.id)
    if nature:
        q = q.filter(LigneBudget.nature == nature)

    comptes = sorted({l.compte for l in q if l.compte})
    return jsonify({"comptes": comptes})


@bp.route("/api/subvention/<int:subvention_id>/lignes")
@login_required
@require_perm("subventions:view")
def api_lignes(subvention_id):
    sub = Subvention.query.get_or_404(subvention_id)
    if not can_see_secteur(sub.secteur):
        abort(403)

    compte = (request.args.get("compte") or "").strip()
    nature = request.args.get("nature")

    q = LigneBudget.query.filter_by(subvention_id=sub.id)
    if nature:
        q = q.filter(LigneBudget.nature == nature)
    if compte:
        q = q.filter(LigneBudget.compte == compte)

    lignes = q.order_by(LigneBudget.compte.asc(), LigneBudget.libelle.asc()).all()

    out = []
    for l in lignes:
        out.append({
            "id": l.id,
            "compte": l.compte,
            "libelle": l.libelle,
            "montant_reel": float(l.montant_reel or 0),
            "engage": float(l.engage or 0),
            "reste": float(l.reste or 0),
        })

    return jsonify({"lignes": out})


@bp.route("/api/global-search")
@login_required
def api_global_search():
    term = (request.args.get("q") or "").strip()
    payload = _run_global_search(term, panel_limit=20, page_limit=100)
    return jsonify({
        "results": payload.get("results", []),
        "query": payload.get("query", term),
        "debug": payload.get("debug", {}),
        "facets": payload.get("facets", {}),
        "meta": payload.get("meta", {}),
    })


@bp.route("/recherche")
@login_required
def global_search_results():
    term = (request.args.get("q") or "").strip()
    selected_type = (request.args.get("type") or "").strip()
    effective_term = term
    if selected_type and f"type:{selected_type.lower()}" not in term.lower():
        effective_term = f"type:{selected_type} {term}".strip()

    payload = _run_global_search(effective_term, panel_limit=100, page_limit=100)
    results = payload.get("all_results") or payload.get("results") or []
    if selected_type:
        results = [item for item in results if (item.get("type") or "").lower() == selected_type.lower()]

    grouped_results = {}
    for item in results:
        group_key = (item.get("type") or "Autres").strip() or "Autres"
        grouped_results.setdefault(group_key, []).append(item)

    context = {
        "query": payload.get("query", term),
        "results": results,
        "items": results,
        "grouped_results": grouped_results,
        "facets": payload.get("facets") if isinstance(payload.get("facets"), dict) else {"types": {}, "secteurs": {}},
        "debug": payload.get("debug") if isinstance(payload.get("debug"), dict) else {},
        "meta": payload.get("meta") if isinstance(payload.get("meta"), dict) else {},
        "selected_type": selected_type,
    }
    try:
        return render_template("search_results.html", **context)
    except Exception:
        current_app.logger.exception("global_search_results render failed for q=%r", term)
        return render_template("search_results_fallback.html", **context), 200


# --------- Stats ---------
@bp.route("/stats")
@login_required
@require_perm("stats:view")
def stats():
    """
    Vue synthèse des budgets avec représentation graphique.

    On peut filtrer par année et/ou secteur via des paramètres GET.
    Responsable de secteur : le filtre secteur est forcé sur son secteur.
    Option : filtre projet (projet_id) pour croiser finance + indicateurs participants.
    """
    has_global_scope = can("stats:view_all") or can("scope:all_secteurs")

    # --- Lecture filtres (année, secteur, projet) ---
    annee_raw = (request.args.get("annee") or "").strip()
    secteur_raw = (request.args.get("secteur") or "").strip()
    projet_id_raw = (request.args.get("projet_id") or "").strip()

    selected_annee: int | None = None
    if annee_raw:
        try:
            selected_annee = int(annee_raw)
        except ValueError:
            selected_annee = None

    selected_secteur: str | None = secteur_raw or None

    selected_projet_id: int | None = None
    if projet_id_raw:
        try:
            selected_projet_id = int(projet_id_raw)
        except ValueError:
            selected_projet_id = None

    # --- Base query ---
    sub_q = Subvention.query.filter_by(est_archive=False)
    proj_q = Projet.query

    # Filtre année
    if selected_annee:
        sub_q = sub_q.filter(Subvention.annee_exercice == selected_annee)

    # Filtre secteur
    if selected_secteur:
        sub_q = sub_q.filter(Subvention.secteur == selected_secteur)
        proj_q = proj_q.filter(Projet.secteur == selected_secteur)

    # Filtre projet (finance)
    if selected_projet_id:
        proj_q = proj_q.filter(Projet.id == selected_projet_id)
        sub_q = sub_q.join(SubventionProjet, SubventionProjet.subvention_id == Subvention.id)                   .filter(SubventionProjet.projet_id == selected_projet_id)

    # Restriction responsable secteur
    if not has_global_scope:
        sub_q = sub_q.filter(Subvention.secteur == current_user.secteur_assigne)
        proj_q = proj_q.filter(Projet.secteur == current_user.secteur_assigne)
        selected_secteur = current_user.secteur_assigne

        # On blind le projet : seulement ceux de son secteur
        if selected_projet_id:
            p_tmp = Projet.query.get(selected_projet_id)
            if not p_tmp or p_tmp.secteur != current_user.secteur_assigne:
                selected_projet_id = None

    subs = sub_q.order_by(Subvention.annee_exercice.desc(), Subvention.nom.asc()).all()
    projets = proj_q.order_by(Projet.nom.asc()).all()

    # Pré-calcul des années disponibles (pour sélecteur)
    all_annees = sorted({s.annee_exercice for s in Subvention.query.filter_by(est_archive=False).all()}, reverse=True)
    all_secteurs = current_app.config.get("SECTEURS", [])

    # --- Totaux globaux ---
    total_recu = round(sum(float(s.montant_recu or 0) for s in subs), 2)
    total_engage = round(sum(float(s.total_engage or 0) for s in subs), 2)
    total_reste = round(sum(float(s.total_reste or 0) for s in subs), 2)

    # --- Agrégation par secteur ---
    by_secteur: dict[str, dict[str, float]] = {}
    for s in subs:
        d = by_secteur.setdefault(s.secteur, {"recu": 0.0, "engage": 0.0, "reste": 0.0})
        d["recu"] += float(s.montant_recu or 0)
        d["engage"] += float(s.total_engage or 0)
        d["reste"] += float(s.total_reste or 0)
    for sec, vals in by_secteur.items():
        vals["recu"] = round(vals.get("recu", 0.0), 2)
        vals["engage"] = round(vals.get("engage", 0.0), 2)
        vals["reste"] = round(vals.get("reste", 0.0), 2)

    # --- Agrégation par compte ---
    by_compte: dict[str, dict[str, float]] = {}
    for s in subs:
        for l in s.lignes:
            d = by_compte.setdefault(l.compte, {"reel": 0.0, "engage": 0.0, "reste": 0.0})
            d["reel"] += float(l.montant_reel or 0)
            d["engage"] += float(l.engage or 0)
            d["reste"] += float(l.reste or 0)
    for comp, vals in by_compte.items():
        vals["reel"] = round(vals.get("reel", 0.0), 2)
        vals["engage"] = round(vals.get("engage", 0.0), 2)
        vals["reste"] = round(vals.get("reste", 0.0), 2)

    # --- Détails par projet ---
    by_projet: list[dict[str, float | str]] = []
    for p in projets:
        by_projet.append({
            "id": p.id,
            "nom": p.nom,
            "secteur": p.secteur,
            "demande": p.total_demande,
            "attribue": p.total_attribue,
            "recu": p.total_recu,
            "reel_lignes": p.total_reel_lignes,
            "engage": p.total_engage,
            "reste": p.total_reste,
        })

    # Valeurs max pour barres proportionnelles
    max_secteur_total = max([v["recu"] + v["engage"] + v["reste"] for v in by_secteur.values()] + [0.0])
    max_compte_total = max([v["reel"] + v["engage"] + v["reste"] for v in by_compte.values()] + [0.0])
    max_projet_total = max([p["recu"] + p["engage"] + p["reste"] for p in by_projet] + [0.0])

    # --- Indicateurs projet (si projet sélectionné) ---
    project_indicators = []
    selected_projet = None

    if selected_projet_id:
        selected_projet = Projet.query.get(selected_projet_id)

    if selected_projet and can_see_secteur(selected_projet.secteur):
        atelier_ids = [lnk.atelier_id for lnk in ProjetAtelier.query.filter_by(projet_id=selected_projet.id).all()]

        # borne temporelle : année si fournie, sinon pas de filtre
        date_min = date_max = None
        if selected_annee:
            date_min = date(selected_annee, 1, 1)
            date_max = date(selected_annee, 12, 31)


        # Valeurs calculées "par défaut" sur l'année sélectionnée (context)
        base_date_min = base_date_max = None
        if selected_annee:
            base_date_min = date(selected_annee, 1, 1)
            base_date_max = date(selected_annee, 12, 31)

        def _compute_participants_metrics(atelier_ids_scope, dmin, dmax):
            out = {
                "participants_uniques": 0,
                "presences_totales": 0,
                "sessions_totales": 0,
                "recurrence_2plus": 0,
            }
            if not atelier_ids_scope:
                return out

            sess_q = SessionActivite.query.filter(SessionActivite.atelier_id.in_(atelier_ids_scope))                 .filter(SessionActivite.is_deleted == False)                 .filter(SessionActivite.statut != "annulee")

            session_date = db.func.coalesce(SessionActivite.date_session, SessionActivite.rdv_date)
            if dmin and dmax:
                sess_q = sess_q.filter(session_date >= dmin).filter(session_date <= dmax)

            out["sessions_totales"] = int(sess_q.count())

            sess_ids = [r[0] for r in sess_q.with_entities(SessionActivite.id).all()]
            if not sess_ids:
                return out

            pres_q = PresenceActivite.query.filter(PresenceActivite.session_id.in_(sess_ids))
            out["presences_totales"] = int(pres_q.count())
            out["participants_uniques"] = int(
                pres_q.with_entities(db.func.count(db.distinct(PresenceActivite.participant_id))).scalar() or 0
            )

            sub = pres_q.with_entities(
                PresenceActivite.participant_id,
                db.func.count(PresenceActivite.id).label("c"),
            ).group_by(PresenceActivite.participant_id).having(db.func.count(PresenceActivite.id) >= 2)
            out["recurrence_2plus"] = int(sub.count())
            return out

        # Finances : charges / produits sur les subventions déjà filtrées (année/secteur/projet)
        dep = 0.0
        rec = 0.0
        for s in subs:
            for l in s.lignes:
                mt = float(l.montant_reel or 0)
                if (l.nature or "").lower() == "charge":
                    dep += mt
                elif (l.nature or "").lower() == "produit":
                    rec += mt
        dep = round(dep, 2)
        rec = round(rec, 2)

        inds = ProjetIndicateur.query.filter_by(projet_id=selected_projet.id, is_active=True)             .order_by(ProjetIndicateur.created_at.asc()).all()

        unit_map = {
            "depenses_totales": "€",
            "recettes_totales": "€",
            "cout_par_participant": "€",
            "cout_par_presence": "€",
        }

        for ind in inds:
            params = ind.params() or {}
            dmin, dmax = _indicator_date_range(params, selected_annee)

            # scope atelier (si défini)
            scope_atelier_ids = list(atelier_ids)
            atelier_id = params.get("atelier_id")
            try:
                if atelier_id:
                    atelier_id_int = int(atelier_id)
                    if atelier_id_int in atelier_ids:
                        scope_atelier_ids = [atelier_id_int]
            except Exception:
                pass

            metrics = _compute_participants_metrics(scope_atelier_ids, dmin, dmax)

            # Valeur selon le code
            val = None
            code = ind.code

            if code in ("participants_uniques", "presences_totales", "sessions_totales", "recurrence_2plus"):
                val = metrics.get(code, 0)

            elif code == "depenses_totales":
                val = dep

            elif code == "recettes_totales":
                val = rec

            elif code == "cout_par_participant":
                u = metrics.get("participants_uniques", 0) or 0
                val = round(dep / u, 2) if u else None

            elif code == "cout_par_presence":
                u = metrics.get("presences_totales", 0) or 0
                val = round(dep / u, 2) if u else None

            # objectifs (optionnels)
            target = params.get("target", None)
            op = params.get("target_op", "ge")
            status = _indicator_target_status(val, target, op)

            project_indicators.append({
                "label": ind.label,
                "code": ind.code,
                "value": val,
                "unit": unit_map.get(ind.code, ""),
                "target": target,
                "target_op": op,
                "status": status,
                "period": (params.get("period") or "context"),
                "start": params.get("start"),
                "end": params.get("end"),
                "atelier_id": params.get("atelier_id"),
            })
        inds = ProjetIndicateur.query.filter_by(projet_id=selected_projet.id, is_active=True).order_by(ProjetIndicateur.created_at.asc()).all()

    return render_template(
        "stats.html",
        total_recu=total_recu,
        total_engage=total_engage,
        total_reste=total_reste,
        by_secteur=by_secteur,
        by_compte=by_compte,
        by_projet=by_projet,
        max_secteur_total=max_secteur_total,
        max_compte_total=max_compte_total,
        max_projet_total=max_projet_total,
        all_annees=all_annees,
        all_secteurs=all_secteurs,
        selected_annee=selected_annee,
        selected_secteur=selected_secteur,
        selected_projet_id=selected_projet_id,
        projets_for_filter=projets,
        selected_projet=selected_projet,
        project_indicators=project_indicators,
    )


# --- Hub ergonomique : 1 menu "Stats & bilans" ---
@bp.route("/stats-bilans")
@login_required
@require_perm("stats:view")
def stats_bilans():
    has_global_scope = can("stats:view_all") or can("scope:all_secteurs")

    annee_raw = (request.args.get("annee") or "").strip()
    secteur_raw = (request.args.get("secteur") or "").strip()
    projet_id_raw = (request.args.get("projet_id") or "").strip()

    selected_annee = None
    if annee_raw:
        try:
            selected_annee = int(annee_raw)
        except ValueError:
            selected_annee = None

    selected_secteur = secteur_raw or None

    selected_projet_id = None
    if projet_id_raw:
        try:
            selected_projet_id = int(projet_id_raw)
        except ValueError:
            selected_projet_id = None

    sub_q = Subvention.query.filter_by(est_archive=False)
    proj_q = Projet.query

    if selected_annee is not None:
        sub_q = sub_q.filter(Subvention.annee_exercice == selected_annee)
    if selected_secteur:
        sub_q = sub_q.filter(Subvention.secteur == selected_secteur)
        proj_q = proj_q.filter(Projet.secteur == selected_secteur)
    if selected_projet_id:
        sub_q = sub_q.join(SubventionProjet, SubventionProjet.subvention_id == Subvention.id)\
                     .filter(SubventionProjet.projet_id == selected_projet_id)
        proj_q = proj_q.filter(Projet.id == selected_projet_id)

    if not has_global_scope:
        selected_secteur = current_user.secteur_assigne
        sub_q = sub_q.filter(Subvention.secteur == selected_secteur)
        proj_q = proj_q.filter(Projet.secteur == selected_secteur)
        if selected_projet_id:
            pjt = Projet.query.get(selected_projet_id)
            if not pjt or pjt.secteur != selected_secteur:
                selected_projet_id = None
                proj_q = Projet.query.filter(Projet.secteur == selected_secteur)

    subs = sub_q.order_by(Subvention.annee_exercice.desc(), Subvention.nom.asc()).all()
    projets = proj_q.order_by(Projet.nom.asc()).all()
    selected_projet = next((p for p in projets if p.id == selected_projet_id), None)

    annees = sorted({s.annee_exercice for s in Subvention.query.filter_by(est_archive=False).all()}, reverse=True)
    secteurs = current_app.config.get("SECTEURS", []) or sorted({s.secteur for s in Subvention.query.filter_by(est_archive=False).all() if s.secteur})
    if not has_global_scope:
        secteurs = [current_user.secteur_assigne]

    total_recu = round(sum(float(s.montant_recu or 0) for s in subs), 2)
    total_engage = round(sum(float(s.total_engage or 0) for s in subs), 2)
    total_reste = round(sum(float(s.total_reste or 0) for s in subs), 2)
    total_demande = round(sum(float(s.montant_demande or 0) for s in subs), 2)

    kpis = {
        "subventions": len(subs),
        "projets": len(projets) if not selected_projet_id else (1 if selected_projet else 0),
        "recu": total_recu,
        "engage": total_engage,
        "reste": total_reste,
        "taux_conso": round((total_engage / total_recu) * 100, 1) if total_recu else 0.0,
    }

    by_secteur = []
    by_sec_map = {}
    for s in subs:
        d = by_sec_map.setdefault(s.secteur or "—", {"secteur": s.secteur or "—", "recu": 0.0, "engage": 0.0, "reste": 0.0})
        d["recu"] += float(s.montant_recu or 0)
        d["engage"] += float(s.total_engage or 0)
        d["reste"] += float(s.total_reste or 0)
    for row in by_sec_map.values():
        row["recu"] = round(row["recu"], 2)
        row["engage"] = round(row["engage"], 2)
        row["reste"] = round(row["reste"], 2)
        by_secteur.append(row)
    by_secteur.sort(key=lambda x: x["recu"], reverse=True)

    top_subventions = []
    for s in sorted(subs, key=lambda x: float(x.montant_recu or 0), reverse=True)[:5]:
        top_subventions.append({
            "nom": s.nom,
            "annee": s.annee_exercice,
            "secteur": s.secteur,
            "recu": round(float(s.montant_recu or 0), 2),
            "engage": round(float(s.total_engage or 0), 2),
            "reste": round(float(s.total_reste or 0), 2),
        })

    alertes = []
    for s in subs:
        recu = float(s.montant_recu or 0)
        reel_lignes = float(s.total_reel_lignes or 0)
        engage = float(s.total_engage or 0)
        if recu > 0 and reel_lignes == 0:
            alertes.append({"niveau": "danger", "texte": f"{s.nom} : reçu {recu:.2f}€ mais lignes réel = 0€ (ventilation manquante)."})
        elif recu > 0 and reel_lignes > 0 and reel_lignes < recu:
            alertes.append({"niveau": "warning", "texte": f"{s.nom} : reçu {recu:.2f}€ mais lignes réel = {reel_lignes:.2f}€ (ventilation incomplète)."})
        elif reel_lignes > 0 and engage > reel_lignes:
            alertes.append({"niveau": "danger", "texte": f"{s.nom} : engagé {engage:.2f}€ > lignes réel {reel_lignes:.2f}€ (dépassement)."})
    alertes = alertes[:5]

    summary = {
        "filters_label": {
            "annee": selected_annee if selected_annee is not None else "toutes",
            "secteur": selected_secteur if selected_secteur else "tous",
            "projet": selected_projet.nom if selected_projet else "tous",
        },
        "total_demande": total_demande,
    }

    return render_template(
        "stats_bilans.html",
        annees=annees,
        secteurs=secteurs,
        projets=projets,
        selected_annee=selected_annee,
        selected_secteur=selected_secteur,
        selected_projet_id=selected_projet_id,
        selected_projet=selected_projet,
        kpis=kpis,
        by_secteur=by_secteur,
        top_subventions=top_subventions,
        alertes=alertes,
        summary=summary,
    )



# --------- Contrôle ---------

@bp.route("/controle", methods=["GET", "POST"])
@login_required
@require_perm("controle:view")
def controle():
    if request.method == "POST":
        action = (request.form.get("action") or "").strip()
        if action == "add_materiel":
            nom = (request.form.get("nom") or "").strip()
            if nom:
                ordre = db.session.query(func.coalesce(func.max(MaterielType.ordre), 0)).scalar() or 0
                db.session.add(MaterielType(nom=nom, ordre=int(ordre) + 10, actif=True))
                db.session.commit()
                flash("Matériel ajouté.", "success")
            else:
                flash("Nom du matériel obligatoire.", "danger")
            return redirect(url_for("main.controle"))
        if action == "toggle_materiel":
            mid = request.form.get("materiel_id", type=int)
            m = MaterielType.query.get_or_404(mid)
            m.actif = not bool(m.actif)
            db.session.commit()
            flash("État du matériel mis à jour.", "success")
            return redirect(url_for("main.controle"))
        if action == "add_conso_config":
            label = (request.form.get("label") or "").strip()
            date_debut = _parse_iso_date(request.form.get("date_debut") or "")
            date_fin = _parse_iso_date(request.form.get("date_fin") or "")
            co2 = request.form.get("co2_kg_par_kwh", type=float) or 0.06

            if date_debut and date_fin and date_fin < date_debut:
                flash("La date de fin ne peut pas être antérieure à la date de début.", "danger")
                return redirect(url_for("main.controle"))

            if not label or not date_debut:
                flash("Label et date de début obligatoires.", "danger")
                return redirect(url_for("main.controle"))

            cfg = MaterielConsommationConfig(
                label=label,
                date_debut=date_debut,
                date_fin=date_fin,
                co2_kg_par_kwh=co2,
                actif=True,
            )
            db.session.add(cfg)
            db.session.flush()

            for m in MaterielType.query.order_by(MaterielType.ordre.asc(), MaterielType.nom.asc()).all():
                watts = request.form.get(f"watts_{m.id}", type=float)
                if watts is not None and watts > 0:
                    db.session.add(MaterielConsommationLigne(config_id=cfg.id, materiel_id=m.id, watts=watts))

            db.session.commit()
            flash("Référentiel de consommation ajouté.", "success")
            return redirect(url_for("main.controle"))

        if action == "update_conso_config":
            cfg_id = request.form.get("config_id", type=int)
            cfg = MaterielConsommationConfig.query.get_or_404(cfg_id)

            label = (request.form.get("label") or "").strip()
            date_debut = _parse_iso_date(request.form.get("date_debut") or "")
            date_fin = _parse_iso_date(request.form.get("date_fin") or "")
            co2 = request.form.get("co2_kg_par_kwh", type=float) or 0.06

            if date_debut and date_fin and date_fin < date_debut:
                flash("La date de fin ne peut pas être antérieure à la date de début.", "danger")
                return redirect(url_for("main.controle"))

            if not label or not date_debut:
                flash("Label et date de début obligatoires.", "danger")
                return redirect(url_for("main.controle"))

            cfg.label = label
            cfg.date_debut = date_debut
            cfg.date_fin = date_fin
            cfg.co2_kg_par_kwh = co2
            cfg.actif = request.form.get("actif") == "1"

            MaterielConsommationLigne.query.filter_by(config_id=cfg.id).delete()
            for m in MaterielType.query.order_by(MaterielType.ordre.asc(), MaterielType.nom.asc()).all():
                watts = request.form.get(f"watts_{m.id}", type=float)
                if watts is not None and watts > 0:
                    db.session.add(MaterielConsommationLigne(config_id=cfg.id, materiel_id=m.id, watts=watts))

            db.session.commit()
            flash("Référentiel de consommation mis à jour.", "success")
            return redirect(url_for("main.controle"))

        if action == "delete_conso_config":
            cfg_id = request.form.get("config_id", type=int)
            cfg = MaterielConsommationConfig.query.get_or_404(cfg_id)

            used_count = SessionActivite.query.filter(SessionActivite.consommation_config_id == cfg.id).count()
            if used_count:
                flash(
                    f"Impossible de supprimer ce référentiel : il est utilisé par {used_count} séance(s). "
                    "Désactive-le ou ajoute une date de fin pour conserver l'historique.",
                    "danger",
                )
                return redirect(url_for("main.controle"))

            MaterielConsommationLigne.query.filter_by(config_id=cfg.id).delete()
            db.session.delete(cfg)
            db.session.commit()
            flash("Référentiel supprimé.", "warning")
            return redirect(url_for("main.controle"))

    materiels = MaterielType.query.order_by(MaterielType.ordre.asc(), MaterielType.nom.asc()).all()
    configs = (
        MaterielConsommationConfig.query
        .order_by(MaterielConsommationConfig.date_debut.desc(), MaterielConsommationConfig.id.desc())
        .all()
    )

    config_rows = []
    for cfg in configs:
        watts_by_materiel = {ln.materiel_id: ln.watts for ln in (cfg.lignes or [])}
        used_count = SessionActivite.query.filter(SessionActivite.consommation_config_id == cfg.id).count()
        config_rows.append({
            "cfg": cfg,
            "watts_by_materiel": watts_by_materiel,
            "used_count": used_count,
        })

    return render_template(
        "controle.html",
        materiels=materiels,
        consommation_configs=configs,
        config_rows=config_rows,
    )


# --------- Bilan financeurs (global) ---------
from sqlalchemy import distinct

@bp.route("/bilan")
@login_required
@require_perm("bilans:view")
def bilan_global():
    payload = _compute_bilan_global_payload()
    return render_template(
        "bilan.html",
        subs=payload["subs"],
        totals=payload["totals"],
        alertes=payload["alertes"],
        secteurs=payload["secteurs"],
        projets=payload["projets"],
        selected_annee=payload["selected_annee"],
        selected_secteur=payload["selected_secteur"],
        selected_projet_id=payload["selected_projet_id"],
    )


@bp.route("/bilan/export.xlsx")
@login_required
@require_perm("bilans:view")
def bilan_global_export_xlsx():
    payload = _compute_bilan_global_payload()
    wb = _build_bilan_global_workbook(payload)
    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)
    secteur_label = (payload["selected_secteur"] or "all").replace(" ", "_")
    annee_label = payload["selected_annee"] or "all"
    return send_file(
        bio,
        as_attachment=True,
        download_name=f"bilan_global_{annee_label}_{secteur_label}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# Alias de compat (si ton layout appelle encore main.bilan)

@bp.route("/bilan-global")
@login_required
def bilan():
    return redirect(url_for("main.bilan_global"))


# --------- Exports simples ---------
@bp.route("/export/depenses.csv")
@login_required
@require_perm("depenses:view")
def export_depenses_csv():
    dep_q = Depense.query.join(LigneBudget).join(Subvention)
    if not can("scope:all_secteurs"):
        dep_q = dep_q.filter(Subvention.secteur == current_user.secteur_assigne)

    deps = dep_q.all()

    out = StringIO()
    writer = csv.writer(out, delimiter=";")
    writer.writerow(["secteur", "subvention", "annee", "compte", "ligne", "depense", "montant", "date_paiement", "type"])

    for d in deps:
        l = d.budget_source
        s = l.source_sub
        writer.writerow([
            s.secteur,
            s.nom,
            s.annee_exercice,
            l.compte,
            l.libelle,
            d.libelle,
            f"{float(d.montant or 0):.2f}".replace(".", ","),
            d.date_paiement.isoformat() if d.date_paiement else "",
            d.type_depense or ""
        ])

    content = out.getvalue().encode("utf-8-sig")  # Excel friendly
    filename = f"depenses_{date.today().isoformat()}.csv"
    return Response(content, mimetype="text/csv", headers={
        "Content-Disposition": f"attachment; filename={filename}"
    })


@bp.route("/export/subvention/<int:subvention_id>.csv")
@login_required
@require_perm("subventions:view")
def export_subvention_csv(subvention_id):
    s = Subvention.query.get_or_404(subvention_id)
    if not can_see_secteur(s.secteur):
        abort(403)

    out = StringIO()
    writer = csv.writer(out, delimiter=";")
    writer.writerow(["subvention", "secteur", "annee", "compte", "ligne", "base", "reel", "engage", "reste"])

    for l in s.lignes:
        writer.writerow([
            s.nom,
            s.secteur,
            s.annee_exercice,
            l.compte,
            l.libelle,
            f"{float(l.montant_base or 0):.2f}".replace(".", ","),
            f"{float(l.montant_reel or 0):.2f}".replace(".", ","),
            f"{float(l.engage or 0):.2f}".replace(".", ","),
            f"{float(l.reste or 0):.2f}".replace(".", ","),
        ])

    content = out.getvalue().encode("utf-8-sig")
    return Response(content, mimetype="text/csv", headers={
        "Content-Disposition": f"attachment; filename=subvention_{s.id}.csv"
    })


# --------- Bilan par subvention ---------
@bp.route("/subvention/<int:subvention_id>/bilan")
@login_required
@require_perm("subventions:view")
def subvention_bilan(subvention_id: int):
    """
    Vue détaillée pour un financeur / subvention.

    Affiche un récapitulatif des montants demandés/attribués/reçus et des lignes de budget,
    avec une représentation graphique proportionnelle par ligne (charges et produits).
    """
    sub = Subvention.query.get_or_404(subvention_id)
    # Vérification des droits : un responsable ne peut consulter que son secteur
    if not can_see_secteur(sub.secteur):
        abort(403)

    # Collecte des lignes de budget
    lignes: list[dict[str, float | str]] = []
    # Calcul du montant maximum utilisé pour la largeur des barres
    max_total = 0.0
    for l in sub.lignes:
        base = float(l.montant_base or 0)
        reel = float(l.montant_reel or 0)
        engage = float(l.engage or 0)
        reste = float(l.reste or 0)
        nature = getattr(l, "nature", "charge")
        total_for_max = reel + engage + reste
        if total_for_max > max_total:
            max_total = total_for_max
        lignes.append({
            "id": l.id,
            "compte": l.compte,
            "libelle": l.libelle,
            "base": base,
            "reel": reel,
            "engage": engage,
            "reste": reste,
            "nature": nature,
        })

    # Calcul des pourcentages pour chaque ligne (évite de surcharger le template)
    if max_total > 0:
        for d in lignes:
            d["p_reel"] = (d["reel"] / max_total) * 100.0 if d["reel"] else 0.0
            d["p_engage"] = (d["engage"] / max_total) * 100.0 if d["engage"] else 0.0
            d["p_reste"] = (d["reste"] / max_total) * 100.0 if d["reste"] else 0.0
    else:
        for d in lignes:
            d["p_reel"] = d["p_engage"] = d["p_reste"] = 0.0

    # Totaux synthétiques (charges et produits séparés)
    totals = {
        "demande": float(sub.montant_demande or 0),
        "attribue": float(sub.montant_attribue or 0),
        "recu": float(sub.montant_recu or 0),
        "base_charges": 0.0,
        "base_produits": 0.0,
        "reel_charges": 0.0,
        "reel_produits": 0.0,
        "engage": 0.0,
        "reste": 0.0,
    }
    for d in lignes:
        if d["nature"] == "produit":
            totals["base_produits"] += d["base"]
            totals["reel_produits"] += d["reel"]
        else:
            totals["base_charges"] += d["base"]
            totals["reel_charges"] += d["reel"]
            totals["engage"] += d["engage"]
            totals["reste"] += d["reste"]

    # Arrondis des totaux
    for k in totals:
        totals[k] = round(float(totals[k] or 0), 2)

    return render_template(
        "subvention_bilan.html",
        sub=sub,
        lignes=lignes,
        totals=totals,
        max_total=max_total,
    )



# ---------------------------------------------------------------------
# RBAC Test (diagnostic)
# ---------------------------------------------------------------------
@bp.route("/rbac-test")
@login_required
@require_perm("admin:rbac")
def rbac_test():
    """Page de diagnostic RBAC.
    Affiche les rôles/perms effectifs de l'utilisateur connecté (et le legacy role si présent).
    """
    from app.models import Permission  # import local pour éviter les cycles

    # Rôles RBAC (selon ton implémentation, role_codes peut être une méthode ou une propriété)
    role_codes_val = []
    if hasattr(current_user, "role_codes"):
        rc = getattr(current_user, "role_codes")
        try:
            role_codes_val = rc() if callable(rc) else list(rc or [])
        except Exception:
            try:
                role_codes_val = list(rc or [])
            except Exception:
                role_codes_val = []

    # legacy role string (compat)
    legacy_role = getattr(current_user, "role", None)

    perms = Permission.query.order_by(Permission.category.asc(), Permission.code.asc()).all()

    has_perm_fn = getattr(current_user, "has_perm", None)
    def _has(code: str) -> bool:
        try:
            return bool(has_perm_fn(code)) if callable(has_perm_fn) else False
        except Exception:
            return False

    perms_by_cat = {}
    for p in perms:
        cat = getattr(p, "category", None) or "Autre"
        perms_by_cat.setdefault(cat, []).append({
            "code": p.code,
            "label": getattr(p, "label", "") or p.code,
            "granted": _has(p.code),
        })

    # stats rapides
    total = sum(len(v) for v in perms_by_cat.values())
    granted = sum(1 for v in perms_by_cat.values() for x in v if x["granted"])

    user_info = {
        "id": getattr(current_user, "id", None),
        "email": getattr(current_user, "email", None),
        "nom": getattr(current_user, "nom", None),
        "secteur_assigne": getattr(current_user, "secteur_assigne", None),
        "legacy_role": legacy_role,
        "role_codes": role_codes_val,
        "perms_total": total,
        "perms_granted": granted,
    }

    return render_template(
        "rbac_test.html",
        user_info=user_info,
        perms_by_cat=perms_by_cat,
        total_perms=total,
        granted_perms=granted,
    )
