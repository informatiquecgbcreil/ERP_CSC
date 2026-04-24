
from __future__ import annotations

from collections import defaultdict
from datetime import date

from app.models import MaterielType, MaterielConsommationConfig, SessionMateriel
from app.extensions import db


def list_materiels_actifs():
    return MaterielType.query.filter_by(actif=True).order_by(MaterielType.ordre.asc(), MaterielType.nom.asc()).all()


def active_config_for_date(target_date: date | None):
    if not target_date:
        return None
    return (
        MaterielConsommationConfig.query
        .filter(MaterielConsommationConfig.actif.is_(True))
        .filter(MaterielConsommationConfig.date_debut <= target_date)
        .filter((MaterielConsommationConfig.date_fin.is_(None)) | (MaterielConsommationConfig.date_fin >= target_date))
        .order_by(MaterielConsommationConfig.date_debut.desc(), MaterielConsommationConfig.id.desc())
        .first()
    )


def _session_date(session):
    return getattr(session, 'rdv_date', None) or getattr(session, 'date_session', None)


def assign_session_config(session):
    target_date = _session_date(session)
    cfg = active_config_for_date(target_date)
    if cfg:
        session.consommation_config_id = cfg.id
    return cfg


def save_session_materiels_from_form(session, form):
    active_ids = {m.id for m in list_materiels_actifs()}
    existing = {sm.materiel_id: sm for sm in getattr(session, 'materiels', [])}
    for materiel_id in active_ids:
        raw = (form.get(f'quantite_{materiel_id}') or '').strip()
        try:
            qty = int(raw or '0')
        except Exception:
            qty = 0
        sm = existing.get(materiel_id)
        if qty > 0:
            if sm:
                sm.quantite = qty
            else:
                db.session.add(SessionMateriel(session_id=session.id, materiel_id=materiel_id, quantite=qty))
        elif sm:
            db.session.delete(sm)


def calculate_session_consumption(session, atelier=None):
    target_date = _session_date(session)
    cfg = getattr(session, 'consommation_config', None) or active_config_for_date(target_date)
    if not cfg:
        return {'config': None, 'total_kwh': 0.0, 'co2_kg': 0.0, 'details': [], 'materiels_count': 0}

    duration_minutes = getattr(session, 'duree_minutes', None)
    if not duration_minutes:
        start = getattr(session, 'rdv_debut', None) or getattr(session, 'heure_debut', None)
        end = getattr(session, 'rdv_fin', None) or getattr(session, 'heure_fin', None)
        if start and end and ':' in start and ':' in end:
            try:
                sh, sm = [int(x) for x in start.split(':', 1)]
                eh, em = [int(x) for x in end.split(':', 1)]
                duration_minutes = max(0, (eh*60+em) - (sh*60+sm))
            except Exception:
                duration_minutes = None
    duration_hours = (duration_minutes or 60) / 60.0
    watt_map = {line.materiel_id: float(line.watts or 0) for line in cfg.lignes}
    details = []
    total = 0.0
    for sm in getattr(session, 'materiels', []) or []:
        watts = watt_map.get(sm.materiel_id, 0.0)
        if watts <= 0 or (sm.quantite or 0) <= 0:
            continue
        kwh = (sm.quantite * watts * duration_hours) / 1000.0
        total += kwh
        details.append({
            'nom': sm.materiel.nom if sm.materiel else f'Matériel #{sm.materiel_id}',
            'quantite': sm.quantite,
            'watts': watts,
            'kwh': round(kwh, 3),
        })
    co2 = total * float(cfg.co2_kg_par_kwh or 0.0)
    return {
        'config': cfg,
        'total_kwh': round(total, 3),
        'co2_kg': round(co2, 3),
        'details': details,
        'materiels_count': sum(int(d['quantite']) for d in details),
    }


def aggregate_sessions_consumption(sessions):
    total_kwh = 0.0
    total_co2 = 0.0
    session_count = 0
    by_materiel = defaultdict(float)
    for s in sessions:
        payload = calculate_session_consumption(s)
        total_kwh += payload['total_kwh']
        total_co2 += payload['co2_kg']
        if payload['details']:
            session_count += 1
        for d in payload['details']:
            by_materiel[d['nom']] += d['kwh']
    top = sorted(by_materiel.items(), key=lambda x: x[1], reverse=True)
    return {
        'total_kwh': round(total_kwh, 2),
        'total_co2': round(total_co2, 2),
        'sessions_count': session_count,
        'avg_kwh_per_session': round(total_kwh / session_count, 3) if session_count else 0.0,
        'top_materiels': [{'nom': n, 'kwh': round(v, 2)} for n, v in top[:5]],
    }
