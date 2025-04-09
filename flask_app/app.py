from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///steps.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class StepsCounter(db.Model):
    date = db.Column(db.String(10), nullable=False, primary_key=True)  # Формат 'YYYY-MM-DD'
    steps = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {"date": self.date, "steps": self.steps}


# Создание базы данных
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")


# Получение всех строк
@app.route("/api/steps", methods=["GET"])
def get_steps():
    steps = StepsCounter.query.all() #список обьектов
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

# Удаление строчки
@app.route("/api/steps/<string:date_step>", methods=["DELETE"])
def delete_step(date_step):
    # Для Date нужно преобразовать строку в дату
    step = StepsCounter.query.get(date_step)
    if not step:
        return jsonify({"error": "Entry not found"}), 404
    db.session.delete(step)
    db.session.commit()
    return jsonify({"message": "Entry deleted successfully"})

if __name__ == "__main__":
    app.run(debug = True, port = 5001)
