

"""Capacited Vehicles Routing Problem (CVRP)."""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from math import radians, cos, sin, asin, sqrt

no_of_records_to_process = 79
no_of_drivers = 4


def read_input_file():
    f = open("order_inputs.csv")
    s = ""
    for i in f:
        s += i
    s = s.split("\n")
    s = s[1:]
    if (s[-1] == ""):
        s = s[:-1]
    a = []
    for i in s:
        j = i.split(",")
        if (len(j) == 3):
            a.append(i.split(","))
    return a[:no_of_records_to_process]

def write(s, filepath):
    f = open(filepath, "w")
    f.write(s)
    f.close()

def haversine(lat1, lat2, lon1, lon2):
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 3956
    return (c * r * 1000) / 0.621  # get in meters
    # return (c * r) # get in miles

def manhattan_distance(a, b):
    dis = abs(a[0] - b[0]) + abs(a[1] - b[1])
    return dis

# o(n^2)
def create_dataset():
    a = read_input_file()
    a = [[ "" , "37.59421314347102", "-77.40944701755696"]] + a
    fin = []
    ord_ids = []
    ord_map = {}
    for i in a:
        ord_ids.append(i[0])
        ord_map[i[0]] = i[1] + "," + i[2]
        te = []
        for j in a:
            te.append(haversine(float(i[1]), float(j[1]), float(i[2]), float(j[2])))
        fin.append(te)
    return fin, ord_ids, ord_map



def create_data_model():
    """Stores the data for the problem."""
    data = {}
    data['distance_matrix'] = create_dataset()[0]
    n = len(data["distance_matrix"])
    data['demands'] = [1] * n
    data['vehicle_capacities'] = [25, 25, 25, 25]
    data['num_vehicles'] = 4
    data['depot'] = 0
    return data, create_dataset()[1], create_dataset()[2]


def print_solution(data, manager, routing, solution):
    batches = []
    """Prints solution on console."""
    print(f'Objective: {solution.ObjectiveValue()}')
    total_distance = 0
    total_load = 0
    for vehicle_id in range(data['num_vehicles']):
        batch = []
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        route_load = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_load += data['demands'][node_index]
            plan_output += ' {0} Load({1}) -> '.format(node_index, route_load)
            batch.append(node_index)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        batches.append(batch)
        plan_output += ' {0} Load({1})\n'.format(manager.IndexToNode(index),
                                                 route_load)
        plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        plan_output += 'Load of the route: {}\n'.format(route_load)
        print(plan_output)
        total_distance += route_distance
        total_load += route_load
    print('Total distance of all routes: {}m'.format(total_distance))
    print('Total load of all routes: {}'.format(total_load))
    return batches


def process(data):
    """Solve the CVRP problem."""
    # Instantiate the data problem.
    # data = create_data_model()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)


    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)


    # Add Capacity constraint.
    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(1)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        return print_solution(data, manager, routing, solution)


if __name__ == '__main__':
    create_dataset()
    a, ord_ids, ord_map = create_data_model()
    batches = process(a)
    print("----------------------------")
    s = ""
    bid = 0
    print("batches", len(batches))
    print(ord_ids)
    for i in batches:
        print(i)
        if (len(i) < 2):
            continue
        bid += 1
        seq = 0
        for _id in i[1:]:
            seq += 1
            s += (ord_ids[_id] + "," + str(bid) + "," + str(seq) + "\n")
    write(s, "out_cap.csv")
