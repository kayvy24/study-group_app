from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

users = []
study_groups = [
    {"id": 1, "class": "Math", "time": "Mornings", "members": [], "deleted": False},
    {"id": 2, "class": "Biology", "time": "Afternoons", "members": [], "deleted": False},
    {"id": 3, "class": "History", "time": "Evenings", "members": [], "deleted": False}
]

@app.route('/')
def index():
    active_groups = [g for g in study_groups if not g["deleted"]]
    return render_template("index.html", groups=active_groups, users=users)

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    subject = request.form['subject']
    time = request.form['time']

    matched = next((g for g in study_groups if g["class"].lower() == subject.lower() and g["time"].lower() == time.lower() and not g["deleted"]), None)

    user = {"name": name, "subject": subject, "time": time, "group_id": matched["id"] if matched else None}
    users.append(user)

    if matched:
        matched["members"].append(name)

    return redirect(url_for('index'))

@app.route('/edit_user/<name>', methods=['GET', 'POST'])
def edit_user(name):
    user = next((u for u in users if u["name"] == name), None)
    if not user:
        return "User not found", 404

    if request.method == 'POST':
        old_group = next((g for g in study_groups if g["id"] == user["group_id"]), None)
        if old_group and user["name"] in old_group["members"]:
            old_group["members"].remove(user["name"])

        user["subject"] = request.form["subject"]
        user["time"] = request.form["time"]

        matched = next((g for g in study_groups if g["class"].lower() == user["subject"].lower() and g["time"].lower() == user["time"].lower() and not g["deleted"]), None)
        user["group_id"] = matched["id"] if matched else None

        if matched:
            matched["members"].append(user["name"])

        return redirect(url_for('index'))

    return render_template("edit_user.html", user=user)

@app.route('/delete_group/<int:group_id>')
def delete_group(group_id):
    group = next((g for g in study_groups if g["id"] == group_id), None)
    if group:
        group["deleted"] = True
    return redirect(url_for('index'))

@app.route('/restore_group/<int:group_id>')
def restore_group(group_id):
    group = next((g for g in study_groups if g["id"] == group_id), None)
    if group:
        group["deleted"] = False
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
