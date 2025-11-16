"""
Provider dashboard routes for Scholarsphere
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user

provider_bp = Blueprint('provider', __name__)

@provider_bp.route('/dashboard')
@login_required
def dashboard():
    """Provider dashboard"""
    if current_user.role != 'provider':
        flash('Access denied. Provider access required.', 'error')
        return redirect(url_for('index'))

    # Build real-time stats from database
    from flask import current_app
    from datetime import datetime, date
    db = current_app.extensions['sqlalchemy']

    # Active and draft scholarships
    active_count = db.session.execute(
        db.text("SELECT COUNT(*) FROM scholarships WHERE provider_id=:pid AND status IN ('approved','active') AND is_active=1"),
        {"pid": current_user.id}
    ).scalar() or 0
    draft_count = db.session.execute(
        db.text("SELECT COUNT(*) FROM scholarships WHERE provider_id=:pid AND status='draft' AND is_active=1"),
        {"pid": current_user.id}
    ).scalar() or 0

    # Applications for this provider's scholarships
    total_apps = db.session.execute(
        db.text("""
            SELECT COUNT(*) FROM scholarship_applications sa
            JOIN scholarships s ON sa.scholarship_id = s.id
            WHERE s.provider_id = :pid AND sa.is_active = 1
        """), {"pid": current_user.id}
    ).scalar() or 0

    # New applications (last 7 days)
    seven_days_ago = datetime.utcnow().isoformat()
    new_apps = db.session.execute(
        db.text("""
            SELECT COUNT(*) FROM scholarship_applications sa
            JOIN scholarships s ON sa.scholarship_id = s.id
            WHERE s.provider_id = :pid AND sa.is_active = 1
              AND sa.application_date >= :since
        """), {"pid": current_user.id, "since": seven_days_ago}
    ).scalar() or 0

    # Pending reviews
    pending_reviews = db.session.execute(
        db.text("""
            SELECT COUNT(*) FROM scholarship_applications sa
            JOIN scholarships s ON sa.scholarship_id = s.id
            WHERE s.provider_id = :pid AND sa.is_active = 1 AND sa.status='pending'
        """), {"pid": current_user.id}
    ).scalar() or 0

    # Reviewed today
    today_str = date.today().isoformat()
    today_reviews = db.session.execute(
        db.text("""
            SELECT COUNT(*) FROM scholarship_applications sa
            JOIN scholarships s ON sa.scholarship_id = s.id
            WHERE s.provider_id = :pid AND sa.reviewed_at IS NOT NULL
              AND substr(CAST(sa.reviewed_at AS TEXT), 1, 10) = :today
        """), {"pid": current_user.id, "today": today_str}
    ).scalar() or 0

    dashboard_data = {
        'user': current_user,
        'stats': {
            'active_scholarships': active_count,
            'draft_scholarships': draft_count,
            'total_applications': total_apps,
            'new_applications': new_apps,
            'pending_reviews': pending_reviews,
            'today_reviews': today_reviews
        }
    }

    return render_template('provider/dashboard.html', data=dashboard_data)

@provider_bp.route('/scholarships')
@login_required
def scholarships():
    """Manage scholarships page"""
    if current_user.role != 'provider':
        flash('Access denied. Provider access required.', 'error')
        return redirect(url_for('index'))
    
    # Load from database
    import sqlite3
    import os
    from datetime import datetime
    db_path = os.path.join(current_app.instance_path, 'scholarsphere.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Load active scholarships
    cursor.execute(
        """
        SELECT id, code, title, deadline, created_at, applications_count, status
        FROM scholarships
        WHERE provider_id = ? AND COALESCE(is_active,1) = 1
        ORDER BY id ASC
        """,
        (current_user.id,)
    )
    active_rows = cursor.fetchall()
    
    # Load archived scholarships
    cursor.execute(
        """
        SELECT id, code, title, deadline, created_at, applications_count, status
        FROM scholarships
        WHERE provider_id = ? AND COALESCE(is_active,0) = 0
        ORDER BY id ASC
        """,
        (current_user.id,)
    )
    archived_rows = cursor.fetchall()
    conn.close()

    def fmt_date(s):
        if not s:
            return ''
        try:
            return datetime.fromisoformat(s.replace('Z','+00:00')).strftime('%b %d, %Y')
        except Exception:
            return s

    def format_scholarship_data(rows):
        return [
            {
                'id': r[1] or f"SCH-{r[0]:03d}",
                'title': r[2],
                'deadline': fmt_date(r[3]),
                'created_date': fmt_date(r[4]),
                'applications': r[5] or 0,
                'status': (r[6] or 'draft').title()
            }
            for r in rows
        ]

    active_scholarships = format_scholarship_data(active_rows)
    archived_scholarships = format_scholarship_data(archived_rows)
    
    return render_template('provider/scholarships.html', 
                         scholarships=active_scholarships, 
                         archived_scholarships=archived_scholarships)

@provider_bp.route('/api/scholarships/<int:scholarship_id>/publish', methods=['POST'])
@login_required
def publish_scholarship(scholarship_id):
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    try:
        import sqlite3
        import os
        db_path = os.path.join(current_app.instance_path, 'scholarsphere.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Ensure ownership
        cursor.execute("SELECT id FROM scholarships WHERE id=? AND provider_id=?", (scholarship_id, current_user.id))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'Scholarship not found'}), 404
        cursor.execute("UPDATE scholarships SET status='approved' WHERE id=?", (scholarship_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@provider_bp.route('/api/publish-by-code', methods=['POST'])
@login_required
def publish_by_code():
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    data = request.get_json() or {}
    code = (data.get('code') or '').strip()
    if not code:
        return jsonify({'success': False, 'error': 'Code required'}), 400
    try:
        import sqlite3
        import os
        db_path = os.path.join(current_app.instance_path, 'scholarsphere.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM scholarships WHERE code=? AND provider_id=?", (code, current_user.id))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({'success': False, 'error': 'Scholarship not found'}), 404
        cursor.execute("UPDATE scholarships SET status='approved' WHERE id=?", (row[0],))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@provider_bp.route('/applications')
@login_required
def applications():
    """Student applications page"""
    if current_user.role != 'provider':
        flash('Access denied. Provider access required.', 'error')
        return redirect(url_for('index'))
    
    # Get actual applications from database using raw SQL
    from flask import current_app
    from datetime import datetime
    try:
        db = current_app.extensions['sqlalchemy']
    except KeyError:
        from app import db
    
    # Fetch applications for scholarships owned by this provider
    applications_query = db.session.execute(
        db.text("""
            SELECT 
                sa.id,
                sa.user_id,
                sa.scholarship_id,
                sa.status,
                sa.application_date,
                u.first_name,
                u.last_name,
                u.email,
                u.student_id,
                s.code,
                s.title as scholarship_title,
                s.deadline,
                (SELECT COUNT(*) FROM scholarship_application_files WHERE application_id = sa.id) as file_count
            FROM scholarship_applications sa
            INNER JOIN scholarships s ON sa.scholarship_id = s.id
            INNER JOIN users u ON sa.user_id = u.id
            WHERE s.provider_id = :provider_id 
            AND sa.is_active = 1
            ORDER BY sa.application_date DESC
        """),
        {"provider_id": current_user.id}
    ).fetchall()
    
    # Group applications by scholarship
    scholarships_dict = {}
    for app in applications_query:
        scholarship_id = app[2]
        
        # Parse application date
        app_date = None
        if app[4]:
            try:
                app_date = datetime.fromisoformat(app[4].replace('Z', '+00:00'))
            except:
                app_date = datetime.now()
        else:
            app_date = datetime.now()
        
        # Parse deadline
        parsed_deadline = None
        if app[11]:
            try:
                parsed_deadline = datetime.fromisoformat(app[11].replace('Z', '+00:00'))
            except:
                parsed_deadline = None
        
        if scholarship_id not in scholarships_dict:
            scholarships_dict[scholarship_id] = {
                'scholarship_code': app[9],
                'scholarship_title': app[10],
                'deadline': parsed_deadline,
                'applications': []
            }
        else:
            # Ensure deadline is set if not yet parsed
            if scholarships_dict[scholarship_id].get('deadline') is None:
                scholarships_dict[scholarship_id]['deadline'] = parsed_deadline
        
        scholarships_dict[scholarship_id]['applications'].append({
            'id': f"APP-{app[0]:03d}",
            'application_id': app[0],
            'student_name': f"{app[5]} {app[6]}",
            'student_email': app[7],
            'student_id': app[8],
            'date_applied': app_date.strftime('%B %d, %Y'),
            'status': (app[3] or 'pending').title(),
            'file_count': app[12] or 0,
            'student_user_id': app[1]
        })
    
    # Convert to list for template
    scholarships_with_applications = []
    for scholarship_id, data in scholarships_dict.items():
        deadline_str = data['deadline'].strftime('%B %d, %Y') if hasattr(data['deadline'], 'strftime') and data['deadline'] else 'No deadline'
        scholarships_with_applications.append({
            'scholarship_id': scholarship_id,
            'code': data['scholarship_code'],
            'title': data['scholarship_title'],
            'deadline': deadline_str,
            'application_count': len(data['applications']),
            'applications': data['applications']
        })
    
    return render_template('provider/applications.html', 
                         scholarships=scholarships_with_applications,
                         total_applications=len(applications_query))

@provider_bp.route('/schedules')
@login_required
def schedules():
    """Scholarship schedules page"""
    if current_user.role != 'provider':
        flash('Access denied. Provider access required.', 'error')
        return redirect(url_for('index'))
    
    # Get actual applications from database
    from flask import current_app
    from datetime import datetime
    try:
        db = current_app.extensions['sqlalchemy']
    except KeyError:
        from app import db
    
    # Fetch applications for scholarships owned by this provider
    applications_query = db.session.execute(
        db.text("""
            SELECT 
                sa.id,
                sa.user_id,
                sa.scholarship_id,
                sa.status,
                sa.application_date,
                u.first_name,
                u.last_name,
                u.email,
                u.student_id,
                u.course,
                u.year_level,
                s.code,
                s.title as scholarship_title
            FROM scholarship_applications sa
            INNER JOIN scholarships s ON sa.scholarship_id = s.id
            INNER JOIN users u ON sa.user_id = u.id
            WHERE s.provider_id = :provider_id 
            AND sa.is_active = 1
            AND sa.status IN ('pending', 'approved')
            ORDER BY sa.application_date DESC
        """),
        {"provider_id": current_user.id}
    ).fetchall()
    
    schedules_data = []
    for app in applications_query:
        # Parse application date
        app_date = None
        if app[4]:
            try:
                app_date = datetime.fromisoformat(app[4].replace('Z', '+00:00'))
            except:
                app_date = datetime.now()
        else:
            app_date = datetime.now()
        
        schedules_data.append({
            'application_id': f"APP-{app[0]:03d}",
            'application_id_raw': app[0],
            'student_name': f"{app[5]} {app[6]}",
            'student_email': app[7],
            'student_id': app[8],
            'course': app[9] or 'Not specified',
            'year_level': app[10] or 'Not specified',
            'scholarship_code': app[11],
            'scholarship_title': app[12],
            'status': (app[3] or 'pending').title(),
            'date_applied': app_date.strftime('%B %d, %Y'),
            'student_user_id': app[1],
            'scholarship_id': app[2]
        })
    
    return render_template('provider/schedules.html', applications=schedules_data)

@provider_bp.route('/report.pdf')
@login_required
def generate_report_pdf():
    """Generate PDF report of scholarships and applicants for this provider"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    try:
        from flask import current_app, send_file
        import io
        from datetime import datetime
        from reportlab.lib.pagesizes import LETTER
        from reportlab.pdfgen import canvas

        db = current_app.extensions['sqlalchemy']
        rows = db.session.execute(
            db.text(
                """
                SELECT s.title, u.first_name, u.last_name, sa.status
                FROM scholarship_applications sa
                JOIN scholarships s ON sa.scholarship_id = s.id
                JOIN users u ON sa.user_id = u.id
                WHERE s.provider_id = :pid AND sa.is_active = 1
                ORDER BY s.title ASC, u.last_name ASC, u.first_name ASC
                """
            ), {"pid": current_user.id}
        ).fetchall()

        # Group by scholarship
        grouped = {}
        for title, fn, ln, status in rows:
            grouped.setdefault(title or 'Untitled Scholarship', []).append((fn or '', ln or '', (status or 'pending').title()))

        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=LETTER)
        width, height = LETTER
        y = height - 50
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Scholarship Applications Report")
        c.setFont("Helvetica", 10)
        y -= 15
        c.drawString(50, y, f"Provider: {current_user.get_full_name()} | {current_user.organization or ''}")
        y -= 15
        c.drawString(50, y, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
        y -= 25

        if not grouped:
            c.drawString(50, y, "No applications found.")
        else:
            for sch_title, applicants in grouped.items():
                if y < 80:
                    c.showPage(); y = height - 50
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y, f"Scholarship: {sch_title}")
                y -= 18
                c.setFont("Helvetica", 10)
                for fn, ln, status in applicants:
                    if y < 60:
                        c.showPage(); y = height - 50
                        c.setFont("Helvetica-Bold", 12)
                        c.drawString(50, y, f"Scholarship: {sch_title} (cont.)")
                        y -= 18
                        c.setFont("Helvetica", 10)
                    c.drawString(60, y, f"- {ln}, {fn}  |  Status: {status}")
                    y -= 14
                y -= 8

        c.showPage()
        c.save()
        buf.seek(0)
        return send_file(buf, mimetype='application/pdf', as_attachment=True, download_name='provider_report.pdf')
    except ModuleNotFoundError:
        return jsonify({'success': False, 'error': 'PDF generation requires reportlab. Install with pip install reportlab.'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@provider_bp.route('/api/application/<int:application_id>/retract', methods=['POST'])
@login_required
def retract_application(application_id):
    """Retract a reviewed application back to pending"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    try:
        from flask import current_app
        from datetime import datetime
        db = current_app.extensions['sqlalchemy']
        row = db.session.execute(
            db.text("""
                SELECT sa.status, sa.user_id, sa.scholarship_id
                FROM scholarship_applications sa
                JOIN scholarships s ON sa.scholarship_id = s.id
                WHERE sa.id = :id AND s.provider_id = :pid
            """), {"id": application_id, "pid": current_user.id}
        ).fetchone()
        if not row:
            return jsonify({'success': False, 'error': 'Application not found'}), 404
        old_status, user_id, scholarship_id = row
        if (old_status or '').lower() == 'pending':
            return jsonify({'success': False, 'error': 'Application is already pending'}), 400
        # Set back to pending
        db.session.execute(
            db.text("UPDATE scholarship_applications SET status='pending', reviewed_at=NULL WHERE id=:id"),
            {"id": application_id}
        )
        # Update counts on scholarship
        if (old_status or '').lower() == 'approved':
            db.session.execute(
                db.text("UPDATE scholarships SET approved_count=COALESCE(approved_count,0)-1, pending_count=COALESCE(pending_count,0)+1 WHERE id=:sid"),
                {"sid": scholarship_id}
            )
        else:
            db.session.execute(
                db.text("UPDATE scholarships SET disapproved_count=COALESCE(disapproved_count,0)-1, pending_count=COALESCE(pending_count,0)+1 WHERE id=:sid"),
                {"sid": scholarship_id}
            )
        # Notify student
        db.session.execute(
            db.text("""
                INSERT INTO notifications (user_id, type, title, message, created_at, is_active)
                VALUES (:uid, 'schedule', 'Application Retracted', 'Your application status was retracted back to pending for further review.', :ts, 1)
            """), {"uid": user_id, "ts": datetime.utcnow().isoformat()}
        )
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        if 'db' in locals():
            db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@provider_bp.route('/documents')
@login_required
def documents():
    """Application documents page"""
    if current_user.role != 'provider':
        flash('Access denied. Provider access required.', 'error')
        return redirect(url_for('index'))
    
    # Get actual applications with documents from database
    from flask import current_app
    from datetime import datetime
    try:
        db = current_app.extensions['sqlalchemy']
    except KeyError:
        from app import db
    
    # Fetch applications with their linked credentials
    applications_query = db.session.execute(
        db.text("""
            SELECT 
                sa.id,
                sa.status,
                u.first_name,
                u.last_name,
                u.email,
                s.code,
                s.title as scholarship_title,
                s.requirements
            FROM scholarship_applications sa
            INNER JOIN scholarships s ON sa.scholarship_id = s.id
            INNER JOIN users u ON sa.user_id = u.id
            WHERE s.provider_id = :provider_id 
            AND sa.is_active = 1
            ORDER BY sa.application_date DESC
        """),
        {"provider_id": current_user.id}
    ).fetchall()
    
    documents_data = []
    for app in applications_query:
        application_id = app[0]
        
        # Get files linked to this application
        files_query = db.session.execute(
            db.text("""
                SELECT saf.requirement_type, c.file_name, c.file_path, c.credential_type
                FROM scholarship_application_files saf
                INNER JOIN credentials c ON saf.credential_id = c.id
                WHERE saf.application_id = :app_id
                ORDER BY saf.requirement_type
            """),
            {"app_id": application_id}
        ).fetchall()
        
        # Format files for display
        submitted_documents = []
        for file in files_query:
            submitted_documents.append({
                'requirement_type': file[0],
                'file_name': file[1],
                'file_path': file[2],
                'credential_type': file[3]
            })
        
        documents_data.append({
            'application_id': f"APP-{application_id:03d}",
            'application_id_raw': application_id,
            'student_name': f"{app[2]} {app[3]}",
            'student_email': app[4],
            'scholarship_code': app[5],
            'scholarship_title': app[6],
            'requirements': app[7] or '',
            'status': (app[1] or 'pending').title(),
            'documents': submitted_documents,
            'document_count': len(submitted_documents),
            'completion_status': 'Complete' if len(submitted_documents) > 0 else 'Incomplete'
        })
    
    return render_template('provider/documents.html', documents=documents_data)


@provider_bp.route('/profile')
@login_required
def profile():
    """Organization profile page - display data using users table under provider's data"""
    if current_user.role != 'provider':
        flash('Access denied. Provider access required.', 'error')
        return redirect(url_for('index'))

    # Load provider data from users table
    try:
        from flask import current_app
        db = current_app.extensions['sqlalchemy']
        row = db.session.execute(
            db.text(
                """
                SELECT id, first_name, last_name, email, organization, created_at, COALESCE(is_active,1)
                FROM users WHERE id = :id AND role = 'provider'
                """
            ), {"id": current_user.id}
        ).fetchone()
        if not row:
            flash('Provider record not found.', 'error')
            return redirect(url_for('provider.dashboard'))

        # Count documents submitted to this provider's scholarships
        doc_count = db.session.execute(
            db.text(
                """
                SELECT COUNT(*)
                FROM scholarship_application_files saf
                INNER JOIN scholarship_applications sa ON saf.application_id = sa.id
                INNER JOIN scholarships s ON sa.scholarship_id = s.id
                WHERE s.provider_id = :pid
                """
            ), {"pid": current_user.id}
        ).scalar() or 0

        profile_data = {
            'id': row[0],
            'first_name': row[1],
            'last_name': row[2],
            'email': row[3],
            'organization': row[4] or 'Not specified',
            'created_at': row[5],
            'is_active': bool(row[6]),
            'documents_submitted': doc_count
        }
    except Exception as e:
        flash('Failed to load profile.', 'error')
        return redirect(url_for('provider.dashboard'))

    return render_template('provider/profile.html', profile=profile_data)

# API endpoints for provider functions
@provider_bp.route('/api/create-scholarship', methods=['POST'])
@login_required
def create_scholarship():
    """Create new scholarship"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    # Validate required fields
    required_fields = ['code', 'title', 'deadline']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'{field} is required'}), 400
    
    try:
        import sqlite3
        import os
        from datetime import datetime
        db_path = os.path.join(current_app.instance_path, 'scholarsphere.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if code already exists
        cursor.execute("SELECT id FROM scholarships WHERE code = ?", (data['code'],))
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'Scholarship code already exists'}), 400
        
        # Insert new scholarship with extended fields if columns exist
        # Insert with extended columns (fallback to basic schema if migration not yet run)
        try:
            cursor.execute("""
                INSERT INTO scholarships (
                    code, title, description, type, level, eligibility,
                    deadline, slots, contact_name, contact_email, contact_phone,
                    requirements, provider_id, status, created_at, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'draft', ?, 1)
            """, (
                data['code'],
                data['title'],
                data.get('description'),
                data.get('type'),
                data.get('level'),
                data.get('eligibility'),
                data['deadline'],
                int(data.get('slots') or 0) if str(data.get('slots') or '').strip().isdigit() else None,
                data.get('contact_name'),
                data.get('contact_email'),
                data.get('contact_phone'),
                (data.get('requirements') or ''),
                current_user.id,
                datetime.utcnow().isoformat()
            ))
        except Exception:
            cursor.execute("""
                INSERT INTO scholarships (code, title, deadline, requirements, provider_id, status, created_at, is_active)
                VALUES (?, ?, ?, ?, ?, 'draft', ?, 1)
            """, (
                data['code'],
                data['title'],
                data['deadline'],
                (data.get('requirements') or ''),
                current_user.id,
                datetime.utcnow().isoformat()
            ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Scholarship created successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@provider_bp.route('/api/scholarship/<scholarship_id>', methods=['GET'])
@login_required
def get_scholarship(scholarship_id):
    """Get scholarship details"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        import sqlite3
        import os
        from datetime import datetime
        db_path = os.path.join(current_app.instance_path, 'scholarsphere.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get scholarship by code (since we're using code as ID in the frontend)
        cursor.execute("""
            SELECT id, code, title, deadline, requirements, status, applications_count, created_at
            FROM scholarships
            WHERE code = ? AND provider_id = ?
        """, (scholarship_id, current_user.id))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'success': False, 'error': 'Scholarship not found'}), 404
        
        def fmt_date(s):
            if not s:
                return ''
            try:
                return datetime.fromisoformat(s.replace('Z','+00:00')).strftime('%Y-%m-%d')
            except Exception:
                return s
        
        # Convert requirements from short codes to descriptive names
        requirements_raw = row[4] or ''
        requirements_display = []
        if requirements_raw:
            from credential_matcher import CredentialMatcher
            req_codes = [req.strip() for req in requirements_raw.split(',') if req.strip()]
            for req_code in req_codes:
                if req_code in CredentialMatcher.REQUIREMENT_MAPPINGS:
                    requirements_display.append(CredentialMatcher.REQUIREMENT_MAPPINGS[req_code][0])
                else:
                    requirements_display.append(req_code)  # Keep custom requirements as-is
        
        scholarship = {
            'id': row[0],
            'code': row[1],
            'title': row[2],
            'deadline': fmt_date(row[3]),
            'requirements': ', '.join(requirements_display),  # Use descriptive names
            'requirements_raw': requirements_raw,  # Keep original for editing
            'status': (row[5] or 'draft').title(),
            'applications': row[6] or 0,
            'created_date': fmt_date(row[7])
        }
        
        return jsonify({'success': True, 'scholarship': scholarship})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@provider_bp.route('/api/scholarship/<scholarship_id>', methods=['PUT'])
@login_required
def update_scholarship(scholarship_id):
    """Update scholarship"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    # Validate required fields
    required_fields = ['code', 'title', 'deadline', 'requirements']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'{field} is required'}), 400
    
    try:
        import sqlite3
        import os
        from datetime import datetime
        db_path = os.path.join(current_app.instance_path, 'scholarsphere.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if scholarship exists and belongs to current provider
        cursor.execute("SELECT id FROM scholarships WHERE code = ? AND provider_id = ?", (scholarship_id, current_user.id))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'Scholarship not found'}), 404
        
        # Check if new code already exists (if code is being changed)
        if data['code'] != scholarship_id:
            cursor.execute("SELECT id FROM scholarships WHERE code = ? AND code != ?", (data['code'], scholarship_id))
            if cursor.fetchone():
                conn.close()
                return jsonify({'success': False, 'error': 'Scholarship code already exists'}), 400
        
        # Update scholarship
        updated = False
        try:
            cursor.execute("""
                UPDATE scholarships 
                SET code = ?, title = ?, description = ?, type = ?, level = ?, eligibility = ?, deadline = ?, slots = ?, contact_name = ?, contact_email = ?, contact_phone = ?, requirements = ?, updated_at = ?
                WHERE code = ? AND provider_id = ?
            """, (
                data['code'],
                data['title'],
                data.get('description'),
                data.get('type'),
                data.get('level'),
                data.get('eligibility'),
                data['deadline'],
                int(data.get('slots') or 0) if str(data.get('slots') or '').strip().isdigit() else None,
                data.get('contact_name'),
                data.get('contact_email'),
                data.get('contact_phone'),
                (data.get('requirements') or ''),
                datetime.utcnow().isoformat(),
                scholarship_id,
                current_user.id
            ))
            updated = cursor.rowcount > 0
        except Exception:
            updated = False
        if not updated:
            cursor.execute("""
                UPDATE scholarships 
                SET code = ?, title = ?, deadline = ?, requirements = ?, updated_at = ?
                WHERE code = ? AND provider_id = ?
            """, (
                data['code'],
                data['title'],
                data['deadline'],
                (data.get('requirements') or ''),
                datetime.utcnow().isoformat(),
                scholarship_id,
                current_user.id
            ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Scholarship updated successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@provider_bp.route('/api/scholarship/<scholarship_id>', methods=['DELETE'])
@login_required
def delete_scholarship(scholarship_id):
    """Archive scholarship (soft delete)"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        import sqlite3
        import os
        db_path = os.path.join(current_app.instance_path, 'scholarsphere.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if scholarship exists and belongs to current provider
        cursor.execute("SELECT id FROM scholarships WHERE code = ? AND provider_id = ?", (scholarship_id, current_user.id))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({'success': False, 'error': 'Scholarship not found'}), 404
        
        # Archive: set is_active=0
        try:
            cursor.execute("UPDATE scholarships SET is_active = 0 WHERE code = ? AND provider_id = ?", (scholarship_id, current_user.id))
        except Exception:
            # If is_active column doesn't exist, fallback to DELETE
            cursor.execute("DELETE FROM scholarships WHERE code = ? AND provider_id = ?", (scholarship_id, current_user.id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Scholarship archived successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@provider_bp.route('/api/scholarship/<scholarship_id>/restore', methods=['POST'])
@login_required
def restore_scholarship(scholarship_id):
    """Restore archived scholarship"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        import sqlite3
        import os
        db_path = os.path.join(current_app.instance_path, 'scholarsphere.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if scholarship exists and belongs to current provider
        cursor.execute("SELECT id FROM scholarships WHERE code = ? AND provider_id = ?", (scholarship_id, current_user.id))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({'success': False, 'error': 'Scholarship not found'}), 404
        
        # Restore: set is_active=1
        cursor.execute("UPDATE scholarships SET is_active = 1 WHERE code = ? AND provider_id = ?", (scholarship_id, current_user.id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Scholarship restored successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@provider_bp.route('/api/scholarship/<scholarship_id>/permanent-delete', methods=['DELETE'])
@login_required
def permanent_delete_scholarship(scholarship_id):
    """Permanently delete scholarship (hard delete)"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        import sqlite3
        import os
        db_path = os.path.join(current_app.instance_path, 'scholarsphere.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if scholarship exists and belongs to current provider
        cursor.execute("SELECT id FROM scholarships WHERE code = ? AND provider_id = ?", (scholarship_id, current_user.id))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({'success': False, 'error': 'Scholarship not found'}), 404
        
        # Check if there are any applications for this scholarship
        cursor.execute("SELECT COUNT(*) FROM scholarship_applications WHERE scholarship_id = ? AND is_active = 1", (row[0],))
        app_count = cursor.fetchone()[0]
        
        if app_count > 0:
            conn.close()
            return jsonify({'success': False, 'error': f'Cannot delete scholarship with {app_count} active application(s). Please archive instead.'}), 400
        
        # Permanent delete: remove from database
        cursor.execute("DELETE FROM scholarships WHERE code = ? AND provider_id = ?", (scholarship_id, current_user.id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Scholarship permanently deleted'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@provider_bp.route('/api/scholarship/<scholarship_id>/report-pdf', methods=['GET'])
@login_required
def generate_scholarship_report_pdf(scholarship_id):
    """Generate PDF report of all students who applied for a specific scholarship"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        from flask import current_app, send_file
        import io
        from datetime import datetime, date
        from reportlab.lib.pagesizes import LETTER
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        
        db = current_app.extensions['sqlalchemy']
        
        # Verify scholarship exists and belongs to current provider
        scholarship = db.session.execute(
            db.text("""
                SELECT id, code, title, type
                FROM scholarships
                WHERE code = :code AND provider_id = :provider_id
            """),
            {"code": scholarship_id, "provider_id": current_user.id}
        ).fetchone()
        
        if not scholarship:
            return jsonify({'success': False, 'error': 'Scholarship not found'}), 404
        
        scholarship_db_id = scholarship[0]
        scholarship_code = scholarship[1]
        scholarship_title = scholarship[2]
        scholarship_type = scholarship[3] or 'Not specified'
        
        # Get all applications for this scholarship (approved, pending, and rejected)
        applications = db.session.execute(
            db.text("""
                SELECT 
                    u.first_name,
                    u.last_name,
                    u.student_id,
                    u.birthday,
                    u.course,
                    u.year_level,
                    sa.application_date,
                    sa.reviewed_at,
                    sa.status
                FROM scholarship_applications sa
                INNER JOIN users u ON sa.user_id = u.id
                WHERE sa.scholarship_id = :scholarship_id
                AND sa.is_active = 1
                AND sa.status IN ('approved', 'pending', 'rejected')
                ORDER BY 
                    CASE sa.status
                        WHEN 'approved' THEN 1
                        WHEN 'pending' THEN 2
                        WHEN 'rejected' THEN 3
                    END,
                    sa.application_date DESC
            """),
            {"scholarship_id": scholarship_db_id}
        ).fetchall()
        
        # Create PDF buffer
        buf = io.BytesIO()
        # Set margins to 0.5 inch as requested
        doc = SimpleDocTemplate(buf, pagesize=LETTER, topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # Light blue color for header (matching the design)
        light_blue = colors.HexColor('#4A90E2')  # Light blue matching the image
        
        # Custom black text style
        black_style = ParagraphStyle(
            'BlackStyle',
            parent=styles['Normal'],
            textColor=colors.black,
            fontSize=9,
            leading=11
        )
        
        # Title style (reduced by 1: 16->15)
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            textColor=colors.black,
            fontSize=15,
            leading=18,
            alignment=TA_CENTER,
            spaceAfter=10
        )
        
        # Header info style
        header_info_style = ParagraphStyle(
            'HeaderInfoStyle',
            parent=styles['Normal'],
            textColor=colors.black,
            fontSize=9,
            leading=11,
            alignment=TA_LEFT,
            spaceAfter=4
        )
        
        # Add title
        story.append(Paragraph(f"Scholarship Applications Report", title_style))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(f"<b>Scholarship:</b> {scholarship_title}", header_info_style))
        story.append(Paragraph(f"<b>Type:</b> {scholarship_type}", header_info_style))
        story.append(Paragraph(f"<b>Generated:</b> {datetime.utcnow().strftime('%B %d, %Y at %I:%M %p')}", header_info_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Prepare table data
        table_data = [['Name', 'Student ID', 'Age', 'Course', 'Year Level', 'Date Applied', 'Date Approve', 'Status', 'Grant type']]
        
        for app in applications:
            first_name = app[0] or ''
            last_name = app[1] or ''
            student_id = app[2] or 'N/A'
            birthday = app[3]
            course = app[4] or 'Not specified'
            year_level = app[5] or 'Not specified'
            application_date = app[6]
            reviewed_at = app[7]
            status = (app[8] or 'pending').title()
            
            # Calculate age from birthday
            age = 'N/A'
            if birthday:
                try:
                    if isinstance(birthday, str):
                        birthday_date = datetime.strptime(birthday, '%Y-%m-%d').date()
                    else:
                        birthday_date = birthday
                    today = date.today()
                    age = str(today.year - birthday_date.year - ((today.month, today.day) < (birthday_date.month, birthday_date.day)))
                except:
                    age = 'N/A'
            
            # Format application date (YYYY-MM-DD format to match design)
            date_applied = 'N/A'
            if application_date:
                try:
                    if isinstance(application_date, str):
                        app_dt = datetime.fromisoformat(application_date.replace('Z', '+00:00'))
                    else:
                        app_dt = application_date
                    date_applied = app_dt.strftime('%Y-%m-%d')
                except:
                    date_applied = 'N/A'
            
            # Format reviewed/approved date (YYYY-MM-DD format to match design)
            date_approved = 'N/A'
            if reviewed_at:
                try:
                    if isinstance(reviewed_at, str):
                        rev_dt = datetime.fromisoformat(reviewed_at.replace('Z', '+00:00'))
                    else:
                        rev_dt = reviewed_at
                    date_approved = rev_dt.strftime('%Y-%m-%d')
                except:
                    date_approved = 'N/A'
            
            full_name = f"{first_name} {last_name}".strip() or 'N/A'
            
            table_data.append([
                full_name,
                student_id,
                age,
                course,
                year_level,
                date_applied,
                date_approved,
                status,
                scholarship_type
            ])
        
        # Create table
        if len(table_data) > 1:  # More than just header
            # Wrap long names in Paragraph objects to enable text wrapping
            # Create a style for name wrapping with font size 7
            name_style = ParagraphStyle(
                'NameStyle',
                parent=black_style,
                textColor=colors.black,
                fontSize=7,
                leading=8,
                wordWrap='LTR',
                spaceBefore=0,
                spaceAfter=0
            )
            
            # Style for other table data with font size 7
            data_style = ParagraphStyle(
                'DataStyle',
                parent=black_style,
                textColor=colors.black,
                fontSize=7,
                leading=8,
                spaceBefore=0,
                spaceAfter=0
            )
            
            wrapped_table_data = [table_data[0]]  # Header row
            
            for row in table_data[1:]:
                # Wrap all columns in Paragraph objects with font size 7
                wrapped_row = [
                    Paragraph(str(row[0]) if row[0] else 'N/A', name_style),  # Name with wrapping
                    Paragraph(str(row[1]) if row[1] else 'N/A', data_style),  # Student ID
                    Paragraph(str(row[2]) if row[2] else 'N/A', data_style),  # Age
                    Paragraph(str(row[3]) if row[3] else 'N/A', data_style),  # Course
                    Paragraph(str(row[4]) if row[4] else 'N/A', data_style),  # Year Level
                    Paragraph(str(row[5]) if row[5] else 'N/A', data_style),  # Date Applied
                    Paragraph(str(row[6]) if row[6] else 'N/A', data_style),  # Date Approved
                    Paragraph(str(row[7]) if row[7] else 'N/A', data_style),  # Status
                    Paragraph(str(row[8]) if row[8] else 'N/A', data_style)   # Scholarship Type
                ]
                wrapped_table_data.append(wrapped_row)
            
            # Adjust column widths - make Name column even wider to prevent overflow
            # Total page width: 8.5 inches, margins: 0.5 each side = 7.5 inches usable
            # Column widths: Name much wider, others optimized to fit
            table = Table(wrapped_table_data, colWidths=[2.2*inch, 0.6*inch, 0.3*inch, 0.6*inch, 0.5*inch, 0.7*inch, 0.7*inch, 0.5*inch, 0.7*inch])
            
            # Determine row backgrounds based on status
            row_styles = []
            for i, row in enumerate(table_data[1:], start=1):  # Skip header row
                status = row[7].lower() if len(row) > 7 else ''
                if status == 'rejected':
                    row_styles.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#ffe0e0')))  # Light pink for rejected
                else:
                    row_styles.append(('BACKGROUND', (0, i), (-1, i), colors.white))  # White for approved/pending
            
            table_style = TableStyle([
                # Header row - light blue background with white text
                ('BACKGROUND', (0, 0), (-1, 0), light_blue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),  # Header font size
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                # Data rows - font size 7 as requested
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 7),  # Font size 7 for table data
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # TOP alignment to handle wrapped text
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 1), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ] + row_styles)
            
            table.setStyle(table_style)
            story.append(table)
        else:
            story.append(Paragraph("No applications found for this scholarship.", black_style))
        
        # Build PDF
        doc.build(story)
        buf.seek(0)
        
        # Generate filename
        safe_title = "".join(c for c in scholarship_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"Scholarship_Report_{scholarship_code}_{safe_title}.pdf"
        
        return send_file(buf, mimetype='application/pdf', as_attachment=True, download_name=filename)
        
    except ModuleNotFoundError:
        return jsonify({'success': False, 'error': 'PDF generation requires reportlab. Install with pip install reportlab.'}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@provider_bp.route('/api/application/<int:application_id>/review', methods=['POST'])
@login_required
def review_application(application_id):
    """Approve or reject an application; notify student and update counts"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    try:
        from flask import current_app
        from datetime import datetime
        db = current_app.extensions['sqlalchemy']
        data = request.get_json() or {}
        action = (data.get('action') or '').strip().lower()
        if action not in ('approve', 'reject'):
            return jsonify({'success': False, 'error': 'Invalid action'}), 400

        # Load application and verify ownership
        row = db.session.execute(
            db.text("""
                SELECT sa.status, sa.user_id, sa.scholarship_id
                FROM scholarship_applications sa
                JOIN scholarships s ON sa.scholarship_id = s.id
                WHERE sa.id = :id AND s.provider_id = :pid AND sa.is_active = 1
            """), {"id": application_id, "pid": current_user.id}
        ).fetchone()
        if not row:
            return jsonify({'success': False, 'error': 'Application not found'}), 404
        old_status, user_id, scholarship_id = row

        if (old_status or '').lower() != 'pending':
            return jsonify({'success': False, 'error': f'Application already {old_status or "reviewed"}'}), 400

        now = datetime.utcnow().isoformat()
        if action == 'approve':
            # Update application to approved
            db.session.execute(
                db.text("""
                    UPDATE scholarship_applications
                    SET status = 'approved', reviewed_at = :now, reviewed_by = :rid
                    WHERE id = :id
                """), {"now": now, "rid": current_user.id, "id": application_id}
            )
            # Update scholarship counts
            db.session.execute(
                db.text("""
                    UPDATE scholarships
                    SET approved_count = COALESCE(approved_count,0) + 1,
                        pending_count = CASE WHEN COALESCE(pending_count,0) > 0 THEN pending_count - 1 ELSE 0 END
                    WHERE id = :sid
                """), {"sid": scholarship_id}
            )
            # Notify student
            db.session.execute(
                db.text("""
                    INSERT INTO notifications (user_id, type, title, message, created_at, is_active)
                    VALUES (:uid, 'approved', 'Application Approved', 'Congratulations! Your application has been approved.', :now, 1)
                """), {"uid": user_id, "now": now}
            )
        else:
            # Reject
            db.session.execute(
                db.text("""
                    UPDATE scholarship_applications
                    SET status = 'rejected', reviewed_at = :now, reviewed_by = :rid
                    WHERE id = :id
                """), {"now": now, "rid": current_user.id, "id": application_id}
            )
            db.session.execute(
                db.text("""
                    UPDATE scholarships
                    SET disapproved_count = COALESCE(disapproved_count,0) + 1,
                        pending_count = CASE WHEN COALESCE(pending_count,0) > 0 THEN pending_count - 1 ELSE 0 END
                    WHERE id = :sid
                """), {"sid": scholarship_id}
            )
            db.session.execute(
                db.text("""
                    INSERT INTO notifications (user_id, type, title, message, created_at, is_active)
                    VALUES (:uid, 'update', 'Application Rejected', 'Your application was not approved at this time.', :now, 1)
                """), {"uid": user_id, "now": now}
            )

        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        if 'db' in locals():
            db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@provider_bp.route('/api/application/<int:application_id>', methods=['GET'])
@login_required
def get_application_details(application_id):
    """Get detailed application information"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        import sqlite3
        import os
        from datetime import datetime
        from flask import current_app
        db = current_app.extensions['sqlalchemy']
        
        # Get application details with student info and scholarship info
        app_query = db.session.execute(
            db.text("""
                SELECT 
                    sa.id,
                    sa.user_id,
                    sa.scholarship_id,
                    sa.status,
                    sa.application_date,
                    sa.notes,
                    u.first_name,
                    u.last_name,
                    u.email,
                    u.student_id,
                    u.course,
                    u.year_level,
                    s.title as scholarship_title,
                    s.code as scholarship_code
                FROM scholarship_applications sa
                INNER JOIN users u ON sa.user_id = u.id
                INNER JOIN scholarships s ON sa.scholarship_id = s.id
                WHERE sa.id = :app_id AND s.provider_id = :provider_id
            """),
            {"app_id": application_id, "provider_id": current_user.id}
        ).fetchone()
        
        if not app_query:
            return jsonify({'success': False, 'error': 'Application not found'}), 404
        
        # Parse application date
        app_date = None
        if app_query[4]:
            try:
                app_date = datetime.fromisoformat(app_query[4].replace('Z', '+00:00'))
            except:
                app_date = datetime.now()
        else:
            app_date = datetime.now()
        
        # Get credential files linked to this application
        credentials = db.session.execute(
            db.text("""
                SELECT saf.requirement_type, c.file_name, c.file_path
                FROM scholarship_application_files saf
                INNER JOIN credentials c ON saf.credential_id = c.id
                WHERE saf.application_id = :app_id
                ORDER BY saf.requirement_type
            """),
            {"app_id": application_id}
        ).fetchall()
        
        credentials_list = []
        for cred in credentials:
            credentials_list.append({
                'requirement_type': cred[0],
                'file_name': cred[1],
                'file_path': cred[2]
            })
        
        return jsonify({
            'success': True,
            'application': {
                'id': app_query[0],
                'student_name': f"{app_query[6]} {app_query[7]}",
                'student_email': app_query[8],
                'student_id': app_query[9],
                'course': app_query[10] or 'Not specified',
                'year_level': app_query[11] or 'Not specified',
                'scholarship_title': app_query[12],
                'scholarship_code': app_query[13],
                'status': (app_query[3] or 'pending').title(),
                'date_applied': app_date.strftime('%B %d, %Y at %I:%M %p'),
                'notes': app_query[5] or ''
            },
            'credentials': credentials_list
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@provider_bp.route('/api/application/<int:application_id>/schedule', methods=['POST'])
@login_required
def create_schedule(application_id):
    """Create schedule (persisted + notify student)"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    try:
        from flask import current_app
        from datetime import datetime
        db = current_app.extensions['sqlalchemy']
        data = request.get_json() or {}
        # Verify ownership
        row = db.session.execute(
            db.text("""
                SELECT sa.user_id FROM scholarship_applications sa
                JOIN scholarships s ON sa.scholarship_id = s.id
                WHERE sa.id=:id AND s.provider_id=:pid
            """), {"id": application_id, "pid": current_user.id}
        ).fetchone()
        if not row:
            return jsonify({'success': False, 'error': 'Application not found'}), 404
        user_id = row[0]

        # Persist schedule via ORM
        from app import Schedule
        from datetime import datetime as dt
        sdate = None
        try:
            sdate = dt.strptime((data.get('schedule_date') or ''), '%Y-%m-%d').date()
        except Exception:
            sdate = None
        new_sched = Schedule(
            application_id=application_id,
            provider_id=current_user.id,
            user_id=user_id,
            schedule_date=sdate,
            schedule_time=(data.get('schedule_time') or '').strip(),
            location=(data.get('location') or '').strip(),
            notes=(data.get('notes') or '').strip(),
            created_at=datetime.utcnow()
        )
        db.session.add(new_sched)

        # Notify student
        msg = f"Interview scheduled on {data.get('schedule_date')} {data.get('schedule_time')} at {data.get('location') or 'TBD'}."
        if (data.get('notes') or '').strip():
            msg += f" Notes: {data.get('notes').strip()}"
        db.session.execute(
            db.text("""
                INSERT INTO notifications (user_id, type, title, message, created_at, is_active)
                VALUES (:uid, 'schedule', 'Interview Scheduled', :msg, :ts, 1)
            """), {"uid": user_id, "msg": msg, "ts": datetime.utcnow().isoformat()}
        )
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        if 'db' in locals():
            db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@provider_bp.route('/api/application/<int:application_id>/announcement', methods=['POST'])
@login_required
def send_announcement(application_id):
    """Send announcement/message to a specific student"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    try:
        from flask import current_app
        from datetime import datetime
        db = current_app.extensions['sqlalchemy']
        data = request.get_json() or {}
        
        # Get title and message
        title = (data.get('title') or '').strip()
        message = (data.get('message') or '').strip()
        
        if not title:
            return jsonify({'success': False, 'error': 'Title is required'}), 400
        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        # Verify ownership - ensure the application belongs to a scholarship owned by this provider
        row = db.session.execute(
            db.text("""
                SELECT sa.user_id, u.first_name, u.last_name
                FROM scholarship_applications sa
                JOIN scholarships s ON sa.scholarship_id = s.id
                JOIN users u ON sa.user_id = u.id
                WHERE sa.id=:id AND s.provider_id=:pid AND sa.is_active=1
            """), {"id": application_id, "pid": current_user.id}
        ).fetchone()
        
        if not row:
            return jsonify({'success': False, 'error': 'Application not found or access denied'}), 404
        
        user_id = row[0]
        student_name = f"{row[1]} {row[2]}"
        
        # Create notification for the student
        db.session.execute(
            db.text("""
                INSERT INTO notifications (user_id, type, title, message, created_at, is_active)
                VALUES (:uid, 'announcement', :title, :msg, :ts, 1)
            """), {
                "uid": user_id, 
                "title": title, 
                "msg": message, 
                "ts": datetime.utcnow().isoformat()
            }
        )
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Announcement sent to {student_name} successfully'
        })
    except Exception as e:
        if 'db' in locals():
            db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@provider_bp.route('/api/announcement/scholarship/<int:scholarship_id>', methods=['POST'])
@login_required
def send_announcement_to_scholarship(scholarship_id):
    """Send announcement to all students who applied to a specific scholarship"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    try:
        from flask import current_app
        from datetime import datetime
        db = current_app.extensions['sqlalchemy']
        data = request.get_json() or {}
        
        # Get title and message
        title = (data.get('title') or '').strip()
        message = (data.get('message') or '').strip()
        
        if not title:
            return jsonify({'success': False, 'error': 'Title is required'}), 400
        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        # Verify scholarship belongs to this provider
        scholarship = db.session.execute(
            db.text("""
                SELECT id, code, title
                FROM scholarships
                WHERE id = :sid AND provider_id = :pid AND is_active = 1
            """), {"sid": scholarship_id, "pid": current_user.id}
        ).fetchone()
        
        if not scholarship:
            return jsonify({'success': False, 'error': 'Scholarship not found or access denied'}), 404
        
        # Get only students with APPROVED applications for this scholarship
        applications = db.session.execute(
            db.text("""
                SELECT DISTINCT sa.user_id, u.first_name, u.last_name
                FROM scholarship_applications sa
                JOIN users u ON sa.user_id = u.id
                WHERE sa.scholarship_id = :sid 
                    AND sa.is_active = 1
                    AND sa.status = 'approved'
            """), {"sid": scholarship_id}
        ).fetchall()
        
        if not applications:
            return jsonify({'success': False, 'error': 'No approved students found for this scholarship. Only students with approved applications will receive announcements.'}), 400
        
        # Create notification for each student
        recipient_count = 0
        now = datetime.utcnow().isoformat()
        for app in applications:
            user_id = app[0]
            db.session.execute(
                db.text("""
                    INSERT INTO notifications (user_id, type, title, message, created_at, is_active)
                    VALUES (:uid, 'announcement', :title, :msg, :ts, 1)
                """), {
                    "uid": user_id,
                    "title": title,
                    "msg": message,
                    "ts": now
                }
            )
            recipient_count += 1
        
        db.session.commit()
        
        scholarship_code = scholarship[1]
        scholarship_title = scholarship[2]
        return jsonify({
            'success': True,
            'message': f'Announcement sent to {recipient_count} student(s) for {scholarship_code}',
            'recipient_count': recipient_count,
            'scholarship': scholarship_title
        })
    except Exception as e:
        if 'db' in locals():
            db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@provider_bp.route('/api/scholarships/list', methods=['GET'])
@login_required
def get_scholarships_list():
    """Get list of scholarships for announcement dropdown"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    try:
        from flask import current_app
        db = current_app.extensions['sqlalchemy']
        
        scholarships = db.session.execute(
            db.text("""
                SELECT s.id, s.code, s.title,
                       (SELECT COUNT(DISTINCT sa.user_id)
                        FROM scholarship_applications sa
                        WHERE sa.scholarship_id = s.id 
                            AND sa.is_active = 1 
                            AND sa.status = 'approved') as applicant_count
                FROM scholarships s
                WHERE s.provider_id = :pid AND s.is_active = 1
                ORDER BY s.code ASC
            """), {"pid": current_user.id}
        ).fetchall()
        
        scholarships_list = []
        for sch in scholarships:
            scholarships_list.append({
                'id': sch[0],
                'code': sch[1],
                'title': sch[2],
                'applicant_count': sch[3] or 0
            })
        
        return jsonify({'success': True, 'scholarships': scholarships_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@provider_bp.route('/api/applications/list', methods=['GET'])
@login_required
def get_applications_list():
    """Get list of applications with student info for announcement dropdown"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    try:
        from flask import current_app
        db = current_app.extensions['sqlalchemy']
        
        applications = db.session.execute(
            db.text("""
                SELECT sa.id, sa.user_id, u.first_name, u.last_name, u.email,
                       s.code as scholarship_code, s.title as scholarship_title
                FROM scholarship_applications sa
                JOIN users u ON sa.user_id = u.id
                JOIN scholarships s ON sa.scholarship_id = s.id
                WHERE s.provider_id = :pid AND sa.is_active = 1
                ORDER BY u.last_name ASC, u.first_name ASC
            """), {"pid": current_user.id}
        ).fetchall()
        
        applications_list = []
        for app in applications:
            applications_list.append({
                'application_id': app[0],
                'user_id': app[1],
                'student_name': f"{app[2]} {app[3]}",
                'student_email': app[4],
                'scholarship_code': app[5],
                'scholarship_title': app[6]
            })
        
        return jsonify({'success': True, 'applications': applications_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@provider_bp.route('/api/announcements/history', methods=['GET'])
@login_required
def get_announcement_history():
    """Get history of announcements sent by this provider"""
    if current_user.role != 'provider':
        return jsonify({'error': 'Access denied'}), 403
    try:
        from flask import current_app
        from datetime import datetime
        db = current_app.extensions['sqlalchemy']
        
        # Get all announcements (notifications with type='announcement') sent to students
        # who have applications to this provider's scholarships
        announcements = db.session.execute(
            db.text("""
                SELECT 
                    n.id,
                    n.title,
                    n.message,
                    n.created_at,
                    u.first_name,
                    u.last_name,
                    u.student_id,
                    s.code as scholarship_code,
                    s.title as scholarship_title
                FROM notifications n
                INNER JOIN users u ON n.user_id = u.id
                INNER JOIN scholarship_applications sa ON sa.user_id = u.id
                INNER JOIN scholarships s ON sa.scholarship_id = s.id
                WHERE n.type = 'announcement'
                    AND n.is_active = 1
                    AND s.provider_id = :pid
                    AND sa.is_active = 1
                ORDER BY n.created_at DESC
                LIMIT 100
            """),
            {"pid": current_user.id}
        ).fetchall()
        
        def humanize(dt):
            if not dt:
                return ''
            now = datetime.utcnow()
            if isinstance(dt, str):
                try:
                    dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
                except:
                    return ''
            diff = now - dt
            s = int(diff.total_seconds())
            if s < 60:
                return f"{s}s ago"
            m = s // 60
            if m < 60:
                return f"{m}m ago"
            h = m // 60
            if h < 24:
                return f"{h}h ago"
            d = h // 24
            return f"{d}d ago"
        
        # Group announcements by title+message+time to identify broadcasts
        history_dict = {}
        history_list = []
        
        for ann in announcements:
            ann_id = ann[0]
            title = ann[1]
            message = ann[2]
            created_at = ann[3]
            student_name = f"{ann[4]} {ann[5]}"
            student_id = ann[6]
            scholarship_code = ann[7]
            scholarship_title = ann[8]
            
            # Parse created_at
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                except:
                    created_at = datetime.now()
            
            # Create unique key (title + message + time within 1 minute = same announcement)
            time_key = created_at.strftime('%Y-%m-%d %H:%M')
            unique_key = f"{title}|{message[:100]}|{time_key}"
            
            if unique_key in history_dict:
                # This is part of a broadcast - add student to recipients
                history_dict[unique_key]['recipients'].append(student_name)
                history_dict[unique_key]['recipient_count'] += 1
            else:
                # New announcement entry
                entry = {
                    'id': ann_id,
                    'title': title,
                    'message': message,
                    'created_at': created_at,
                    'time_ago': humanize(created_at),
                    'scholarship_code': scholarship_code,
                    'scholarship_title': scholarship_title,
                    'recipients': [student_name],
                    'recipient_count': 1,
                    'is_broadcast': False
                }
                history_dict[unique_key] = entry
                history_list.append(entry)
        
        # Update broadcast status and format recipients
        for entry in history_list:
            if entry['recipient_count'] > 1:
                entry['is_broadcast'] = True
                entry['recipients_display'] = f"{entry['recipient_count']} students"
            else:
                entry['recipients_display'] = entry['recipients'][0] if entry['recipients'] else 'Unknown'
        
        # Sort by most recent
        history_list.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({'success': True, 'announcements': history_list[:50]})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

