import logging
import traceback

from flask import Flask, render_template, request, make_response, jsonify

from config.config import API_PORT
from engie.base_prod_plan import ProductionPlanCalculator
import json
app = Flask(__name__)

@app.route('/')
def payload():
    return render_template('payload_input.html')


@app.route('/result', methods=['POST','GET'])
def result():
    """
    calculates and gives the results after processing payload input.
    """
    if request.method == 'POST':
        payload = request.form["Name"]
        f = open('example_payloads/{0}.json'.format(payload), "r")
        # Reading from file
        request_data = json.loads(f.read())
    load = request_data.get('load', None)
    fuels = request_data.get('fuels', None)
    powerplants = request_data.get('powerplants', None)
    if not (load and fuels and powerplants):
        return make_response(jsonify({'message': 'Invalid or missing request parameters'}), 400)
    try:
        response_data = ProductionPlanCalculator(load=load,
                                                fuels=fuels,
                                                powerplants=powerplants).get_production_plan()
    except Exception as e:
        logging.error('Error in generating results, Request: {0}, Error: {1}, Message{2}'.format(
            request_data, e.args, e.message))
        logging.error(traceback.format_exc())
        return make_response(jsonify({'Error Message': "{0}".format(e.message)}), 500)
    return make_response(jsonify(response_data), 200)
    # still work remaining to show output in result.html
    # return render_template("result.html", result = response_data[0])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(API_PORT), debug=True)