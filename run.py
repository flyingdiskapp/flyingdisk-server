from app import create_app
from config import Config

app = create_app()

def run_app():
    app.run(debug=False)

if __name__ == '__main__':
    run_app()