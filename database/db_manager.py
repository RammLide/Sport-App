import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect("sport_tracker.db")
        self.create_tables()
        self.populate_initial_data()

    def create_tables(self):
        cursor = self.conn.cursor()
        # Пользователи
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        """)
        # Профиль пользователя
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id INTEGER PRIMARY KEY,
                weight REAL,
                height REAL,
                age INTEGER,
                gender TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        # Типы тренировок
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                met REAL
            )
        """)
        # Упражнения
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                type_id INTEGER,
                met REAL,
                FOREIGN KEY (type_id) REFERENCES training_types(id)
            )
        """)
        # Тренировки
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trainings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date TEXT,
                type_id INTEGER,
                duration INTEGER,
                calories REAL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (type_id) REFERENCES training_types(id)
            )
        """)
        # Упражнения в тренировке
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                training_id INTEGER,
                exercise_id INTEGER,
                sets INTEGER,
                reps INTEGER,
                weight REAL,
                distance REAL,
                pace REAL,
                FOREIGN KEY (training_id) REFERENCES trainings(id),
                FOREIGN KEY (exercise_id) REFERENCES exercises(id)
            )
        """)
        # Питание
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nutrition (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date TEXT,
                food_name TEXT,
                calories REAL,
                protein REAL,
                fat REAL,
                carbs REAL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        # Достижения
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT,
                date TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        # Шаблоны тренировок
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT,
                type TEXT,
                duration INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        # Упражнения в шаблонах
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS template_exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER,
                name TEXT,
                sets INTEGER,
                reps INTEGER,
                weight REAL,
                distance REAL,
                pace REAL,
                FOREIGN KEY (template_id) REFERENCES training_templates(id)
            )
        """)
        # Новая таблица: Гидратация
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hydration (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date TEXT,
                amount REAL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS calendar (
                user_id INTEGER,
                date TEXT,
                note TEXT,
                plan TEXT,
                training_type TEXT,
                training_duration INTEGER,
                hydration_amount REAL,
                completed INTEGER,
                PRIMARY KEY (user_id, date),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        self.conn.commit()

    def populate_initial_data(self):
        cursor = self.conn.cursor()
        # Проверяем, есть ли уже типы тренировок
        cursor.execute("SELECT COUNT(*) FROM training_types")
        if cursor.fetchone()[0] > 0:
            return  # Если данные уже есть, не заполняем

        # Типы тренировок
        training_types = [
            ("Силовая", 6.0), ("Бег", 7.0), ("Велосипед", 8.0), ("Плавание", 7.0),
            ("Ходьба", 4.0), ("Бокс", 9.0), ("Теннис", 7.0), ("Йога", 3.0),
            ("Гимнастика", 4.0), ("Функциональная", 8.0)
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO training_types (name, met) VALUES (?, ?)",
            training_types
        )
        self.conn.commit()

        # Упражнения
        exercises = []

        # Силовая
        silovaya = [
            ("Жим штанги лежа", 6.0), ("Жим штанги на наклонной скамье", 6.0),
            ("Жим гантелей лежа", 5.5), ("Разводка гантелей лежа", 5.0),
            ("Жим штанги стоя", 6.5), ("Жим гантелей сидя", 6.0),
            ("Тяга штанги в наклоне", 6.0), ("Тяга гантели одной рукой", 5.5),
            ("Становая тяга", 6.5), ("Румынская тяга", 6.0),
            ("Приседания со штангой", 6.5), ("Фронтальные приседания", 6.0),
            ("Жим ногами в тренажере", 5.5), ("Разгибания ног в тренажере", 5.0),
            ("Сгибания ног в тренажере", 5.0), ("Подтягивания", 7.0),
            ("Отжимания на брусьях", 6.5), ("Скручивания на пресс", 4.5),
            ("Подъем ног в висе", 5.0), ("Гиперэкстензия", 5.0),
            ("Жим штанги лежа узким хватом", 6.0), ("Жим гантелей на наклонной скамье 30°", 5.5),
            ("Разводка гантелей стоя", 5.0), ("Тяга блока к груди", 5.5),
            ("Тяга блока за голову", 5.5), ("Становая тяга с гантелями", 6.0),
            ("Приседания с гантелями", 5.5), ("Выпады со штангой", 6.0),
            ("Выпады с гантелями", 5.5), ("Жим одной гантели стоя", 6.0),
            ("Тяга вертикального блока", 5.5), ("Жим Арнольда", 6.0),
            ("Французский жим", 5.5), ("Подъем штанги на бицепс", 5.5),
            ("Молотковый подъем гантелей", 5.5), ("Разгибание рук на блоке", 5.0),
            ("Сведение рук в тренажере (бабочка)", 5.0), ("Жим в тренажере Смита", 5.5),
            ("Тяга горизонтального блока", 5.5), ("Ягодичный мостик", 5.5),
            ("Болгарские сплит-приседания", 6.0), ("Подъем на носки в тренажере", 5.0),
            ("Скручивания на наклонной скамье", 4.5), ("Планка с утяжелением", 5.0),
            ("Тяга сумо", 6.5), ("Жим ногами с узкой постановкой", 5.5),
            ("Подтягивания узким хватом", 7.0), ("Отжимания с узкой постановкой", 6.0),
            ("Махи гантелями в стороны", 5.0), ("Тяга штанги к подбородку", 5.5),
            ("Жим штанги на горизонтальной скамье", 6.0),
            ("Разводка гантелей на наклонной скамье", 5.0),
            ("Тяга Т-штанги", 6.0),
            ("Подтягивания обратным хватом", 7.0),
            ("Приседания с гирей (гоблет)", 6.0),
            ("Становая тяга на одной ноге с гантелями", 5.5),
            ("Жим гантелей над головой стоя", 6.0),
            ("Подъем гантелей через стороны", 5.0),
            ("Концентрированный подъем на бицепс", 5.0),
            ("Разгибание рук с гантелью над головой", 5.0),
            ("Подъем штанги на грудь", 6.5),
            ("Тяга гири к подбородку", 6.0),
            ("Скручивания с блином", 4.5),
            ("Русский твист с гантелью", 4.5),
            ("Планка с подтягиванием колена", 5.0),
            ("Махи гирей одной рукой", 6.0),
            ("Тяга блока к поясу сидя", 5.5),
            ("Жим ногами с широкой постановкой", 5.5),
            ("Подъем на носки со штангой", 5.0),
            ("Отведение ноги в тренажере", 5.0),
        ]
        exercises.extend([(ex, 1, met) for ex, met in silovaya])

        # Бег
        beg = [
            ("Бег на дорожке", 7.0), ("Бег на улице", 7.5),
            ("Спринт", 10.0), ("Интервальный бег", 9.0),
            ("Бег в гору", 8.5), ("Бег трусцой", 6.0),
            ("Бег с ускорением", 8.0), ("Бег на месте", 5.5),
            ("Бег с высоким подниманием колен", 7.5), ("Бег с захлестом", 7.0),
            ("Фартлек", 8.5), ("Бег по пересеченной местности", 8.0),
            ("Бег с утяжелителями", 8.5), ("Бег по песку", 9.0),
            ("Бег по лестнице", 8.5), ("Бег с барьерами", 8.0),
            ("Челночный бег", 8.5), ("Бег на короткие дистанции", 9.0),
            ("Бег на длинные дистанции", 7.0), ("Бег с прыжками", 8.0),
        ]
        exercises.extend([(ex, 2, met) for ex, met in beg])

        # Велосипед
        velosiped = [
            ("Езда на велотренажере", 8.0), ("Езда на шоссейном велосипеде", 8.5),
            ("Езда на горном велосипеде", 9.0), ("Спринт на велосипеде", 10.0),
            ("Езда в гору", 9.5), ("Езда по пересеченной местности", 8.5),
            ("Велотренировка с интервалами", 9.0), ("Медленная езда", 6.0),
            ("Езда с сопротивлением", 8.5), ("Велотренировка стоя", 9.0),
            ("Велоспуск", 8.5), ("Езда на тандеме", 7.5),
            ("Велотренировка с высокой каденцией", 8.0), ("Езда по грунтовой дороге", 8.5),
            ("Велотренировка с низким сопротивлением", 7.0), ("Езда с рюкзаком", 8.5),
            ("Велотренировка на треке", 9.0), ("Езда против ветра", 8.5),
            ("Велотренировка с ускорениями", 9.0), ("Езда в группе", 8.0),
        ]
        exercises.extend([(ex, 3, met) for ex, met in velosiped])

        # Плавание
        plavanie = [
            ("Плавание кролем", 7.0), ("Плавание на спине", 6.5),
            ("Плавание брассом", 6.0), ("Плавание баттерфляем", 8.0),
            ("Интервальное плавание", 7.5), ("Плавание с ластами", 6.5),
            ("Плавание с доской", 6.0), ("Плавание вольным стилем", 7.0),
            ("Спринт в бассейне", 8.5), ("Плавание на выносливость", 6.5),
            ("Плавание с поплавком", 6.0), ("Плавание с гантелями", 7.0),
            ("Плавание с сопротивлением", 7.5), ("Плавание на открытой воде", 7.5),
            ("Плавание с поворотами", 7.0), ("Плавание с нырянием", 7.5),
            ("Плавание с высокой интенсивностью", 8.0), ("Плавание с медленным темпом", 6.0),
            ("Плавание с дыхательными упражнениями", 6.5), ("Плавание в стиле дельфин", 7.5),
        ]
        exercises.extend([(ex, 4, met) for ex, met in plavanie])

        # Ходьба
        hodba = [
            ("Ходьба в быстром темпе", 4.5), ("Ходьба в среднем темпе", 4.0),
            ("Ходьба в гору", 5.5), ("Скандинавская ходьба", 5.0),
            ("Ходьба с утяжелителями", 5.0), ("Ходьба по пересеченной местности", 4.5),
            ("Ходьба на дорожке", 4.0), ("Интервальная ходьба", 4.5),
            ("Ходьба с высоким шагом", 4.5), ("Ходьба назад", 4.0),
            ("Ходьба по песку", 5.5), ("Ходьба с палками", 5.0),
            ("Ходьба по лестнице", 5.5), ("Ходьба с рюкзаком", 5.0),
            ("Ходьба по снегу", 5.5), ("Ходьба с длинным шагом", 4.5),
            ("Ходьба по мягкой поверхности", 5.0), ("Ходьба с ускорениями", 4.5),
            ("Ходьба по наклонной дорожке", 5.0), ("Ходьба с боковыми шагами", 4.5),
        ]
        exercises.extend([(ex, 5, met) for ex, met in hodba])

        # Бокс
        boks = [
            ("Удары по груше", 9.0), ("Спарринг", 9.5),
            ("Теневой бой", 8.0), ("Удары по лапам", 8.5),
            ("Прыжки со скакалкой", 8.0), ("Удары в прыжке", 9.0),
            ("Комбинации ударов", 8.5), ("Уклоны и защита", 7.5),
            ("Бокс с утяжелителями", 9.0), ("Скоростные удары", 8.5),
            ("Работа на пневмогруше", 8.5), ("Удары с гантелями", 8.5),
            ("Бокс с тенью", 8.0), ("Удары по манекену", 8.5),
            ("Тренировка реакции", 7.5), ("Бокс с эспандерами", 8.5),
            ("Удары по двойной груше", 8.5), ("Тренировка ног", 7.5),
            ("Комбинации с перемещением", 8.5), ("Бокс на ринге", 9.0),
        ]
        exercises.extend([(ex, 6, met) for ex, met in boks])

        # Теннис
        tennis = [
            ("Подача", 7.5), ("Удар с лета", 7.0),
            ("Удар слева", 7.0), ("Удар справа", 7.0),
            ("Смеш", 7.5), ("Игра у сетки", 7.0),
            ("Тренировка подач", 6.5), ("Игра на задней линии", 7.0),
            ("Интервальный теннис", 7.5), ("Удары с вращением", 7.0),
            ("Топспин", 7.0), ("Бэкхенд", 7.0),
            ("Укороченный удар", 6.5), ("Лоб", 6.5),
            ("Тренировка с пушкой", 7.5), ("Игра на грунте", 7.0),
            ("Игра на траве", 7.0), ("Тренировка с тренером", 7.5),
            ("Удары с полулёта", 7.0), ("Тренировка перемещений", 7.0),
        ]
        exercises.extend([(ex, 7, met) for ex, met in tennis])

        # Йога
        yoga = [
            ("Поза собаки мордой вниз", 3.0), ("Поза воина I", 3.5),
            ("Поза дерева", 2.5), ("Поза моста", 3.0),
            ("Поза кобры", 3.0), ("Поза ребенка", 2.5),
            ("Скручивание сидя", 3.0), ("Поза лотоса", 2.5),
            ("Поза планки", 4.0), ("Поза треугольника", 3.0),
            ("Поза воина II", 3.5), ("Поза голубя", 3.0),
            ("Поза лодки", 3.5), ("Поза ворона", 4.0),
            ("Поза рыбы", 3.0), ("Поза колеса", 4.0),
            ("Поза верблюда", 3.5), ("Поза стула", 3.5),
            ("Поза орла", 3.5), ("Поза наклона вперед", 3.0),
        ]
        exercises.extend([(ex, 8, met) for ex, met in yoga])

        # Гимнастика
        gimnastika = [
            ("Отжимания", 6.0), ("Приседания без веса", 5.0),
            ("Планка", 4.5), ("Берпи", 8.0),
            ("Прыжки звездочкой", 7.0), ("Подтягивания обратным хватом", 7.0),
            ("Скручивания", 4.5), ("Подъем ног лежа", 5.0),
            ("Махи ногами", 4.5), ("Стойка на руках", 6.5),
            ("Прыжки с подтягиванием колен", 7.0), ("Обратные отжимания", 6.0),
            ("Планка с подъемом ноги", 5.0), ("Супермен", 5.0),
            ("Прыжки на одной ноге", 6.5), ("Боковая планка", 5.0),
            ("Скручивания велосипед", 5.0), ("Прыжки через скакалку", 7.0),
            ("Подъем корпуса лежа", 5.0), ("Мостик", 5.5),
        ]
        exercises.extend([(ex, 9, met) for ex, met in gimnastika])

        # Функциональная
        funkcional = [
            ("Бурпи", 8.0), ("Прыжки на ящик", 7.5),
            ("Тяга гири", 7.0), ("Махи гирей", 7.5),
            ("Канат", 8.0), ("Тренировка с TRX", 7.0),
            ("Фермерская прогулка", 7.0), ("Броски медбола", 7.5),
            ("Прыжки через препятствия", 7.5), ("Скручивания с медболом", 6.5),
            ("Тяга санок", 7.5), ("Прыжки с гирей", 7.5),
            ("Тренировка с босу", 7.0), ("Броски мяча в стену", 7.5),
            ("Тяга с резиной", 7.0), ("Прыжки с утяжелением", 7.5),
            ("Тренировка с сэндбэгом", 7.5), ("Скручивания с гирей", 7.0),
            ("Прыжки через канат", 7.5), ("Тренировка с кольцами", 7.5),
        ]
        exercises.extend([(ex, 10, met) for ex, met in funkcional])

        cursor.executemany(
            "INSERT OR IGNORE INTO exercises (name, type_id, met) VALUES (?, ?, ?)",
            exercises
        )
        self.conn.commit()

    def get_hydration_stats(self, user_id, start_date, end_date):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT SUM(amount)
            FROM hydration
            WHERE user_id = ? AND date BETWEEN ? AND ?
            """,
            (user_id, start_date, end_date)
        )
        total = cursor.fetchone()[0] or 0
        return total

    def add_user(self, username, password):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def get_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, username FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        return cursor.fetchone()

    def update_user_profile(self, user_id, weight, height, age, gender):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO user_profiles (user_id, weight, height, age, gender)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, weight, height, age, gender)
        )
        self.conn.commit()

    def get_user_profile(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT weight, height, age, gender FROM user_profiles WHERE user_id = ?",
            (user_id,)
        )
        return cursor.fetchone()

    def add_exercise_if_not_exists(self, name, type_id, met=6.0):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM exercises WHERE name = ? AND type_id = ?", (name, type_id))
        result = cursor.fetchone()
        if result:
            print(f"Exercise '{name}' already exists with ID: {result[0]}")
            return result[0]
        cursor.execute(
            """
            INSERT INTO exercises (name, type_id, met)
            VALUES (?, ?, ?)
            """,
            (name, type_id, met)
        )
        self.conn.commit()
        cursor.execute("SELECT last_insert_rowid()")
        new_id = cursor.fetchone()[0]
        print(f"Created new exercise '{name}' with ID: {new_id}")
        return new_id

    def add_training(self, user_id, date, type_id, duration, calories):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO trainings (user_id, date, type_id, duration, calories)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, date, type_id, duration, calories)
        )
        training_id = cursor.lastrowid
        self.conn.commit()
        return training_id

    def add_training_exercise(self, training_id, exercise_id, sets, reps, weight, distance, pace):
        cursor = self.conn.cursor()
        try:
            print(f"Inserting into training_exercises: training_id={training_id}, exercise_id={exercise_id}, sets={sets}, reps={reps}, weight={weight}, distance={distance}, pace={pace}")
            cursor.execute(
                """
                INSERT INTO training_exercises (training_id, exercise_id, sets, reps, weight, distance, pace)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (training_id, exercise_id, sets, reps, weight, distance, pace)
            )
            self.conn.commit()
            cursor.execute("SELECT last_insert_rowid()")
            inserted_id = cursor.fetchone()[0]
            print(f"Inserted training_exercise ID: {inserted_id}")
            return inserted_id
        except Exception as e:
            print(f"Error in add_training_exercise: {str(e)}")
            self.conn.rollback()
            raise

    def get_training_types(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM training_types")
        return cursor.fetchall()

    def get_exercises_by_type(self, type_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, name FROM exercises WHERE type_id = ?",
            (type_id,)
        )
        return cursor.fetchall()

    def get_training(self, training_id):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT t.type_id, t.duration, t.calories, tt.name
            FROM trainings t
            JOIN training_types tt ON t.type_id = tt.id
            WHERE t.id = ?
            """,
            (training_id,)
        )
        return cursor.fetchone()
    
    def get_training_by_id(self, training_id):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, user_id, type_id, duration, calories
            FROM trainings
            WHERE id = ?
            """,
            (training_id,)
        )
        return cursor.fetchone()

    def get_training_exercises(self, training_id):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT e.name, te.sets, te.reps, te.weight, te.distance, te.pace, te.exercise_id
            FROM training_exercises te
            JOIN exercises e ON te.exercise_id = e.id
            WHERE te.training_id = ?
            """,
            (training_id,)
        )
        results = cursor.fetchall()
        print(f"get_training_exercises for training_id={training_id}: {results}")
        return results

    def update_training(self, training_id, type_id, duration, calories):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE trainings
            SET type_id = ?, duration = ?, calories = ?
            WHERE id = ?
            """,
            (type_id, duration, calories, training_id)
        )
        self.conn.commit()

    def delete_training_exercises(self, training_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM training_exercises WHERE training_id = ?",
            (training_id,)
        )
        self.conn.commit()

    def delete_training(self, training_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM training_exercises WHERE training_id = ?", (training_id,))
        cursor.execute("DELETE FROM trainings WHERE id = ?", (training_id,))
        self.conn.commit()

    def get_trainings_by_date(self, user_id, date):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT t.id, tt.name, t.duration, t.calories
            FROM trainings t
            JOIN training_types tt ON t.type_id = tt.id
            WHERE t.user_id = ? AND t.date = ?
            """,
            (user_id, date)
        )
        return cursor.fetchall()

    def get_training_stats(self, user_id, start_date, end_date):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT tt.name, SUM(t.duration), SUM(t.calories)
            FROM trainings t
            JOIN training_types tt ON t.type_id = tt.id
            WHERE t.user_id = ? AND t.date BETWEEN ? AND ?
            GROUP BY tt.name
            """,
            (user_id, start_date, end_date)
        )
        return cursor.fetchall()

    def add_nutrition(self, user_id, date, food_name, calories, protein, fat, carbs):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO nutrition (user_id, date, food_name, calories, protein, fat, carbs)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, date, food_name, calories, protein, fat, carbs)
        )
        self.conn.commit()

    def get_nutrition_stats(self, user_id, start_date, end_date):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT SUM(calories), SUM(protein), SUM(fat), SUM(carbs)
            FROM nutrition
            WHERE user_id = ? AND date BETWEEN ? AND ?
            """,
            (user_id, start_date, end_date)
        )
        return cursor.fetchone()

    def add_achievement(self, user_id, name):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO achievements (user_id, name, date)
            VALUES (?, ?, ?)
            """,
            (user_id, name, datetime.now().strftime("%Y-%m-%d"))
        )
        self.conn.commit()

    def add_training_template(self, user_id, name, type, duration, exercises):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO training_templates (user_id, name, type, duration)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, name, type, duration)
        )
        template_id = cursor.lastrowid
        for ex in exercises:
            cursor.execute(
                """
                INSERT INTO template_exercises (template_id, name, sets, reps, weight, distance, pace)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (template_id, ex["name"], ex["sets"], ex["reps"], ex["weight"], ex["distance"], ex["pace"])
            )
        self.conn.commit()
        return template_id

    def get_training_templates(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, name, type, duration FROM training_templates WHERE user_id = ? OR user_id IS NULL",
            (user_id,)
        )
        return cursor.fetchall()

    def get_template_exercises(self, template_id):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT name, sets, reps, weight, distance, pace
            FROM template_exercises WHERE template_id = ?
            """,
            (template_id,)
        )
        return cursor.fetchall()
    
    def delete_template(self, user_id, name):
        cursor = self.conn.cursor()
        # Получаем ID шаблона
        cursor.execute(
            """
            SELECT id
            FROM training_templates
            WHERE user_id = ? AND name = ?
            """,
            (user_id, name)
        )
        template = cursor.fetchone()
        if not template:
            return

        template_id = template[0]
        # Удаляем упражнения шаблона
        cursor.execute(
            "DELETE FROM template_exercises WHERE template_id = ?",
            (template_id,)
        )
        # Удаляем сам шаблон
        cursor.execute(
            "DELETE FROM training_templates WHERE id = ?",
            (template_id,)
        )
        self.conn.commit()

    def get_template_by_name(self, user_id, name):
        cursor = self.conn.cursor()
        # Получаем данные шаблона
        cursor.execute(
            """
            SELECT id, user_id, name, type, duration
            FROM training_templates
            WHERE user_id = ? AND name = ?
            """,
            (user_id, name)
        )
        template = cursor.fetchone()
        if not template:
            return None

        # Извлекаем упражнения для шаблона
        template_id = template[0]
        exercises = self.get_template_exercises(template_id)
        return template + (exercises,)
    
    def get_last_training(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, date, type_id, duration, calories
            FROM trainings
            WHERE user_id = ?
            ORDER BY date DESC
            LIMIT 1
            """,
            (user_id,)
        )
        return cursor.fetchone()

    def close(self):
        self.conn.close()