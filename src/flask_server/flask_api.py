from flask_restful import Api, Resource, reqparse
from src.main import start_processing


class ApiHandler(Resource):

    def post(self):
        print(self)

        parser = reqparse.RequestParser()
        parser.add_argument('x', type=float)
        parser.add_argument('img', type=str)
        #parser.add_argument('tileLon', type=float)
        #parser.add_argument('tileLat', type=float)

        args = parser.parse_args()

        print(args)

        grammar = start_processing(args["img"], args["x"])

        final_ret = {"status": "Success", "message": grammar}

        return final_ret
