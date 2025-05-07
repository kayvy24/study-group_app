# app.py
from flask import Flask, render_template, request, redirect, url_for
from models import db, User, StudyGroup

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///studygroup.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.form

    all_groups = StudyGroup.query.filter_by(deleted=False).all()
    best_group = None
    best_score = -1

    # Step 1: Score each group
    for group in all_groups:
        score = 0
        if data['accounting_class'].lower() in group.accounting_class.lower():
            score += 3
        if data['preferred_time'].lower() in group.preferred_time.lower():
            score += 2
        if data['preferred_days'].lower() in group.preferred_days.lower():
            score += 2
        if data['meeting_type'].lower() == group.meeting_type.lower():
            score += 2
        if data['campus'].lower() in group.campus_location.lower():
            score += 1
        if data['group_size'] == group.preferred_group_size or data['group_size'] == "Doesn't matter":
            score += 1

        if score > best_score:
            best_score = score
            best_group = group

    # Step 2: Respect auto-create toggle
    allow_create = data['allow_auto_create'].lower() == 'yes'

    # Threshold to consider it a good match
    MIN_SCORE = 5

    # Step 3: Handle matching logic
    if best_score >= MIN_SCORE:
        matched_group = best_group
    elif allow_create:
        # Create a new group using user’s preferences
        matched_group = StudyGroup(
            accounting_class=data['accounting_class'],
            preferred_time=data['preferred_time'],
            preferred_days=data['preferred_days'],
            meeting_type=data['meeting_type'],
            campus_location=data['campus'],
            preferred_group_size=data['group_size']
        )
        db.session.add(matched_group)
        db.session.commit()
    else:
        # No good match and no auto-create allowed: assign best available even if weak
        matched_group = best_group if best_group else None

    # Step 4: Create user
    user = User(
        name=data['name'],
        accounting_class=data['accounting_class'],
        preferred_time=data['preferred_time'],
        preferred_days=data['preferred_days'],
        group_size=data['group_size'],
        meeting_type=data['meeting_type'],
        campus=data['campus'],
        study_group=matched_group
    )

    db.session.add(user)
    # END of /add_user route — after user is added to DB
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('confirmation', user_id=user.id))








@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        for field in ['accounting_class', 'preferred_time', 'preferred_days', 'group_size', 'meeting_type', 'campus']:
            setattr(user, field, request.form[field])
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_user.html', user=user)

@app.route('/groups')
def list_groups():
    groups = StudyGroup.query.all()
    return render_template('groups.html', groups=groups)

@app.route('/delete_group/<int:group_id>')
def delete_group(group_id):
    group = StudyGroup.query.get_or_404(group_id)
    group.deleted = True
    db.session.commit()
    return redirect(url_for('list_groups'))

@app.route('/restore_group/<int:group_id>')
def restore_group(group_id):
    group = StudyGroup.query.get_or_404(group_id)
    group.deleted = False
    db.session.commit()
    return redirect(url_for('list_groups'))

@app.route('/confirmation/<int:user_id>')
def confirmation(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('confirmation.html', user=user)


if __name__ == '__main__':
    app.run(debug=True)
