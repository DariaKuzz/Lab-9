from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///steps.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class StepsCounter(db.Model):
    date = db.Column(db.String(10), nullable=False, primary_key=True)
    steps = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {"date": self.date, "steps": self.steps}

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/steps", methods=["GET"])
def get_steps():
    steps = StepsCounter.query.all()
    return jsonify([step.to_dict() for step in steps])

@app.route("/api/steps", methods=["POST"])
def add_step():
    try:
        data = request.get_json()
        
        if not data or "date" not in data or "steps" not in data:
            return jsonify({"error": "Требуются date и steps"}), 400

        try:
            datetime.strptime(data["date"], "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Неверный формат даты. Используйте YYYY-MM-DD"}), 400

        if StepsCounter.query.get(data["date"]):
            return jsonify({"error": "Запись на эту дату уже существует"}), 400

        new_step = StepsCounter(
            date=data["date"],
            steps=int(data["steps"])
        )
        
        db.session.add(new_step)
        db.session.commit()
        
        return jsonify({
            "message": "Успешно добавлено",
            "data": new_step.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/api/steps/<string:date_step>", methods=["DELETE"])
def delete_step(date_step):
    step = StepsCounter.query.get(date_step)
    if not step:
        return jsonify({"error": "Entry not found"}), 404
    db.session.delete(step)
    db.session.commit()
    return jsonify({"message": "Entry deleted successfully"})

# Новый endpoint для суммы шагов
@app.route("/api/steps/total")
def get_total_steps():
    try:
        total = db.session.query(db.func.coalesce(db.func.sum(StepsCounter.steps), 0)).scalar()
        return jsonify({"total_steps": total})
    except Exception as e:
        print(f"Ошибка при вычислении суммы: {str(e)}")
        return jsonify({"total_steps": 0, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)