__test_constants = {
    'batch_shape': [(1,), (2,), (5,), (5, 2, 3)],
    'event_shape': [(2,), (3,), (3, 5, 2)],
    'image_shape': [(3, 4, 4), (3, 20, 20), (3, 10, 20), (1, 20, 20), (1, 10, 20)],
    'context_shape': [None, (2,), (3,), (3, 5, 2)],
    'input_event_shape': [(2,), (3,), (3, 5, 2)],
    'output_event_shape': [(2,), (3,), (3, 5, 2)],
    'n_predicted_parameters': [1, 2, 10, 50],
    'predicted_parameter_shape': [(1,), (2,), (5,), (5, 2, 3)],
    'parameter_shape_per_element': [(1,), (2,), (5,), (5, 2, 3)],
    'data_atol': 1e-3,
    'data_atol_easy': 1e-2,
    'log_det_atol': 1e-3,
    'log_det_atol_easy': 1e-2,
}
