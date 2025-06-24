import psycopg2 as pg
from psycopg2 import sql
from nicegui import ui

POSTGRES_CONFIG = {
    "host": "db",
    "port": 5432,
    "database": "pet_vote_demo",
    "user": "postgres",
    "password": "example",
}

APP_CONFIG = {"is_dark": True}


def read_results() -> dict:
    with pg.connect(**POSTGRES_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT pet, COUNT(*) as total FROM results GROUP BY pet")
            rows = cur.fetchall()
            return rows


def save_result(choice: str):
    assert choice in ["dog", "cat"]
    with pg.connect(**POSTGRES_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO results (pet) VALUES (%s)", (choice,))
            conn.commit()
    print(f"Your choice was {choice}")


def create_database(db_name: str, db_config: dict):
    create_database_query = sql.SQL(f"CREATE database {db_name}")
    conn = pg.connect(**db_config)
    cursor = conn.cursor()
    conn.autocommit = True  #!
    cursor.execute(create_database_query)
    cursor.close()
    conn.autocommit = False  #!
    conn.close()


def create_table(db_name: str, db_config: dict):
    create_table_query = sql.SQL(
        """
        CREATE TABLE IF NOT EXISTS results (
            id SERIAL PRIMARY KEY,
            pet VARCHAR(10) NOT NULL
        );
    """
    )
    updated_db_config = {"database": db_name, **db_config}
    with pg.connect(**updated_db_config) as conn:
        with conn.cursor() as cur:
            cur.execute(create_table_query)
            conn.commit()
    print("Database created")


@ui.page("/", dark=APP_CONFIG["is_dark"])
def root_page():
    ui.markdown(
        """
        # Pet Vote Demo
    """
    )
    ui.link("If you haven't set up the database yet go here", "/setup")
    ui.link("If you have already set up the database go vote", "/vote")


@ui.page("/setup", dark=APP_CONFIG["is_dark"])
def setup():
    db_less_config = POSTGRES_CONFIG.copy()
    db_name = db_less_config.pop("database")
    create_database(db_name, db_less_config)
    create_table(db_name, db_less_config)

    ui.markdown(
        """
        # Pet Vote Demo
    """
    )

    ui.link("Voting", "/vote")
    ui.link("Results", "/results")


@ui.page("/vote", dark=APP_CONFIG["is_dark"])
def root_page():
    def choose_dogs():
        save_result("dog")
        ui.notify("You voted for Dogs. Good choice!")

    def choose_cats():
        save_result("cat")
        ui.notify("You voted for Cats but We can still be friends.")

    ui.label("Please vote for your favourite, cats or dogs!")
    ui.label("There is a right answer, and there will be a test later")
    with ui.row():
        ui.button("DOGS", on_click=choose_dogs)
        ui.button("CATS", on_click=choose_cats)
    ui.link("Results", "/results")


@ui.page("/results", dark=APP_CONFIG["is_dark"])
def results_page():
    results = read_results()

    ui.label("Results")
    for result in results:
        ui.label(f"{result[0]}: {result[1]}")

    ui.link("Feel free to go back an vote again!", "/vote")


ui.run(port=5050)
