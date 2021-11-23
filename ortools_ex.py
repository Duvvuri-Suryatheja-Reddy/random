from math import radians, cos, sin, asin, sqrt

from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

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
    fin = []
    ord_ids = []
    ord_map = {}
    for i in a:
        ord_ids.append(i[0])
        ord_map[i[0]] = i[1] + "," + i[2]
        te = []
        for j in a:
            p1 = (float(i[1]), float(i[2]))
            p2 = (float(j[1]), float(j[2]))
            te.append(haversine(float(i[1]), float(j[1]), float(i[2]), float(j[2])))

        fin.append(te)
    return fin, ord_ids, ord_map


def create_data_model():
    """Stores the data for the problem."""
    data = {}
    data['distance_matrix'] = create_dataset()[0]
    # print(data["distance_matrix"])
    data['num_vehicles'] = no_of_drivers
    data['depot'] = 0
    return data, create_dataset()[1], create_dataset()[2]


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    print(f'Objective: {solution.ObjectiveValue()}')
    max_route_distance = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        while not routing.IsEnd(index):
            plan_output += ' {} -> '.format(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += '{}\n'.format(manager.IndexToNode(index))
        plan_output += 'Distance of the route: {}\n'.format(route_distance)
        print(plan_output)
        max_route_distance = max(route_distance, max_route_distance)
    print('Maximum of the route distances: {}'.format(max_route_distance))


def return_batches(data, manager, routing, solution):
    """Prints solution on console."""
    print(f'Objective: {solution.ObjectiveValue()}')
    max_route_distance = 0
    batches = []
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        batch = []
        while not routing.IsEnd(index):
            plan_output += ' {} -> '.format(manager.IndexToNode(index))
            batch.append(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        batches.append(batch)
        plan_output += '{}\n'.format(manager.IndexToNode(index))
        plan_output += 'Distance of the route: {}\n'.format(route_distance)
        print(plan_output)
        max_route_distance = max(route_distance, max_route_distance)
    print('Maximum of the route distances: {}'.format(max_route_distance))
    return batches


def process(data):
    """Entry point of the program."""
    # Instantiate the data problem.
    # data = create_dummy_data_model()

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

    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        3000000,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        return return_batches(data, manager, routing, solution)
    else:
        print('No solution found !')


if __name__ == '__main__':
    create_dataset()
    a, ord_ids, ord_map = create_data_model()
    batches = process(a)
    print("----------------------------")
    s = ""
    bid = 0
    print("batches", len(batches))
    for i in batches:
        print(i)
        if (len(i) < 2):
            continue
        bid += 1
        seq = 0
        for _id in i:
            seq += 1
            s += (ord_ids[_id] + "," + str(bid) + "," + str(seq) + "\n")
    write(s, "out.csv")
