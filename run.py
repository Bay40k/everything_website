# import predict
import app
import waitress


def main():
    waitress.serve(app.app, port=5000, threads=8, expose_tracebacks=True)


if __name__ == "__main__":
    main()
