from functools import wraps
from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from models import db, Participant, Log, Announcement

volunteer_bp = Blueprint('volunteer', __name__)


def volunteer_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') not in ('admin', 'volunteer'):
            # Detect AJAX/Fetch
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
               'application/json' in request.headers.get('Accept', ''):
                return jsonify({'success': False, 'message': 'Session expired. Please log in again.'}), 401
            
            flash('Volunteer access required.', 'error')
            return redirect(url_for('auth.login', role='volunteer'))
        return f(*args, **kwargs)
    return decorated


@volunteer_bp.route('/')
@volunteer_required
def dashboard():
    announcements = Announcement.query.filter(
        Announcement.role_target.in_(['all', 'volunteer'])
    ).order_by(Announcement.created_at.desc()).all()
    return render_template('volunteer/dashboard.html', announcements=announcements)


# ─── Smart Entry/Exit Toggle ───────────────────────────────────────────────────
@volunteer_bp.route('/scan', methods=['POST'])
@volunteer_required
def scan():
    """
    Auto-toggle: if participant is outside → mark entry.
                 if participant is inside  → mark exit.
    """
    try:
        uid = request.form.get('uid', '').strip().upper()
        if not uid:
            return jsonify({'success': False, 'message': 'No ID provided.'}), 400
            
        p = Participant.query.filter_by(unique_id=uid).first()
        if not p:
            return jsonify({'success': False, 'message': f'ID {uid} not found.'}), 404

        if p.is_inside:
            # Mark exit
            p.is_inside = False
            action = 'exit'
            msg = f'{p.name} ({p.unique_id}) exited the venue.'
        else:
            # Mark entry
            p.is_inside = True
            action = 'entry'
            msg = f'{p.name} ({p.unique_id}) entered the venue.'

        log = Log(participant_id=p.id, action=action, note=msg)
        db.session.add(log)
        db.session.commit()

        team = p.team_obj
        members = []
        if team:
            members = [m.to_dict(basic=True) for m in team.members.order_by(Participant.member_number).all()]

        return jsonify({
            'success': True,
            'action': action,
            'message': msg,
            'participant': p.to_dict(),
            'team_name': team.team_name if team else 'Individual',
            'domain': team.domain if team else 'N/A',
            'team_members': members
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Internal error: {str(e)}'}), 500


# ─── Food Scan ─────────────────────────────────────────────────────────────────
@volunteer_bp.route('/food-scan', methods=['POST'])
@volunteer_required
def food_scan():
    try:
        uid = request.form.get('uid', '').strip().upper()
        meal = request.form.get('meal', 'General').strip()
        
        if not uid:
            return jsonify({'success': False, 'message': 'No ID provided.'}), 400
            
        p = Participant.query.filter_by(unique_id=uid).first()
        if not p:
            return jsonify({'success': False, 'message': f'ID {uid} not found.'}), 404
        
        # Check if food already collected for THIS meal TODAY
        from datetime import datetime, date
        today = date.today()
        # Look for a log with action 'food' and note containing the meal name on this day
        existing_log = Log.query.filter(
            Log.participant_id == p.id,
            Log.action == 'food',
            Log.note.ilike(f'%{meal}%'),
            db.func.date(Log.timestamp) == today
        ).first()

        if existing_log:
            return jsonify({
                'success': False,
                'message': f'{p.name} has already collected {meal} today.'
            }), 400

        p.food_issued = True
        p.food_count = (p.food_count or 0) + 1
        msg = f'{meal} token issued to {p.name} ({p.unique_id}). Total: {p.food_count}'
        
        log = Log(participant_id=p.id, action='food', note=msg)
        db.session.add(log)
        db.session.commit()
        
        team = p.team_obj
        members = []
        if team:
            members = [m.to_dict(basic=True) for m in team.members.order_by(Participant.member_number).all()]

        return jsonify({
            'success': True,
            'action': 'food',
            'meal': meal,
            'message': msg,
            'participant': p.to_dict(),
            'team_name': team.team_name if team else 'Individual',
            'domain': team.domain if team else 'N/A',
            'team_members': members
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Internal error: {str(e)}'}), 500
