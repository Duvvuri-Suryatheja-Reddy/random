As a last-mile delivery service, Point Pickup Technologies has an interest in finding optimal, or near-optimal batching algorithms. These algorithms consume an array of orders, 
along with additional data points such as the location of the order and perhaps some constraints, and output an ID & sequence for each order. One driver should deliver all orders with the same batch ID in the sequence provided. Given these inputs, can you devise an efficient algorithm that is able to batch these orders? 

Files:
`order_inputs.csv`:
`order_id`: primary key of this table, an order that needs to be delivered at a certain location
`drop_latitude`: the latitude of the location that the order needs to be delivered at
`drop_longitude`: the longitude of the location that the order needs to be delivered at

`batch_outputs.csv`:
`order_id`: same as `order_inputs.csv`
`batch_id`: orders with the same batch_id are to be delivered consecutively by one-vehicle
`sequence`: the order in which the batched orders should be delivered


Objective:
1. Write a function that computes the distance, in miles, of two latitude / longitude coordinates (feel free to google this problem, it is very well researched)
2. Write a function that consumes `batch_id`, `sequence`, `drop_latitude`, `drop_longitude` inputs and outputs the total distance of the route in miles
3. Compute the total mileage of the solution provided in `batch_outputs.csv` (merge the coordinates from `order_inputs.csv`)
4. Write a function that consumes `order_id`, `drop_latitude`, `drop_longitude` and outputs order_id-batch_id pairs along with a sequence number for each while trying to minimize the output of the function from 2.
5. Use the function from 2. to compare your solution with the output of 3.
6. Describe the time complexity of your solution

Constraints:
1. Assume a maximum size of any batch (make this a parameter to the function). For this exercise, use max_batch_size=25
2. Assume no limit to the number of batches
3. Assume that the distance for the first sequence in a batch is computed from the starting coordinates `37.59421314347102`, `-77.40944701755696`

Things to keep in mind:
1. Solutions should all process within 1 minute using typical hardware
2. We will also test your program on a new dataset to ensure it works with new datapoints

Good luck!
