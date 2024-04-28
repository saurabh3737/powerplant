from engie.constants import FUEL_POWERPLANT_MAPPING, GAS, KEROSINE, WIND

class ProductionPlanCalculator:
    """
    this class is used for calculations based on the input load fuels and powerplants
    in a given production plan.
    """

    def __init__(self, load, fuels, powerplants):
        self.load = load
        self.prices = {}
        self.wind_strength = 0
        self.power_plants = []

        self.set_fuel_details(fuels)
        self.set_power_plants(powerplants)
        self.set_merit_power_plant()

    def set_fuel_details(self, fuel_prices):
        """
        set the fuel details
        """
        for fuel, value in fuel_prices.items():
            if fuel not in FUEL_POWERPLANT_MAPPING.keys():
                continue
            if fuel == WIND:
                self.wind_strength = value
            self.prices[FUEL_POWERPLANT_MAPPING[fuel]] = value
        self.prices[FUEL_POWERPLANT_MAPPING[WIND]] = 0

    def set_power_plants(self, powerplants):
        """
        sets power plant arguments
        """
        for powerplant_type in FUEL_POWERPLANT_MAPPING.values():
            self.power_plants += [PowerPlantBaseDetails(name=powerplant.get('name'),
                                             type=powerplant.get('type'),
                                             efficiency=powerplant.get('efficiency'),
                                             pmin=powerplant.get('pmin'),
                                             pmax=powerplant.get('pmax'),
                                             price=self.prices[powerplant_type],
                                             wind_strength=self.wind_strength)
                                  for powerplant in powerplants if powerplant.get('type') == powerplant_type]

    def set_merit_power_plant(self):
        """
        based on the merit this function set the order
        """
        self.power_plants.sort(key=lambda x: (x.cost, x.pmax * -1), reverse=False)

    def get_production_plan(self):
        """
        Creates and returns the production plan.
        """
        production_plan = []
        remaining_load = self.load

        for power_plant in self.power_plants:
            if remaining_load <= 0:
                production_plan.append({'name': power_plant.name, 'p': 0.0}) # setting  power plants with p=0.0
                continue
            if power_plant.pmax < 0.1:
                continue
            if power_plant.pmin > remaining_load and len(production_plan) > 0:
                energy_excess = power_plant.pmin - remaining_load
                for x in production_plan[::-1]:
                    cur_powerplant = [p for p in self.power_plants if p.name == x.get('name')][0]
                    cur_p = x.get('p')
                    room_to_reduce = cur_p - cur_powerplant.pmin
                    if room_to_reduce > 0.0:
                        if room_to_reduce >= energy_excess:
                            x['p'] = cur_p - energy_excess
                            remaining_load += energy_excess
                            break
                        x['p'] = cur_p - room_to_reduce
                        remaining_load += energy_excess
                        energy_excess -= room_to_reduce
                        break
                    else:
                        continue
            if power_plant.pmax >= remaining_load:
                production_plan.append({'name': power_plant.name, 'p': remaining_load})
                remaining_load = 0
                continue
            production_plan.append({'name': power_plant.name, 'p': power_plant.pmax})
            remaining_load -= power_plant.pmax
        return production_plan

class PowerPlantBaseDetails:
    """
    A PowerPlant based details object for cost calculation
    """

    def __init__(self, name, type, efficiency, pmin, pmax, price=0, wind_strength=0):
        self.name = name
        self.type = type
        self.efficiency = efficiency
        self.pmin = pmin * 1.0
        self.pmax = pmax * 1.0
        self.price = price
        if type == 'windturbine':
            self.pmax = round(self.pmax * (wind_strength / 100), 1)
        self.cost = None
        self.__set_cost()

    def __set_cost(self):
        """
        Sets the cost of the power plant.
        """
        try:
            self.cost = self.price / self.efficiency
        except ZeroDivisionError:
            self.cost = 0
