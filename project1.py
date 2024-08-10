import math


# Function to collect input from the user for traffic volume and lane count at each turn
def get_traffic_volume_and_lanes():
    access_1_turns = ['straight', 'right']
    access_2_turns = ['straight', 'left']
    access_3_turns = ['left', 'right']
    traffic_volume = []
    lanes = []
    free_rights = []

    print("Please enter the traffic volume (number of vehicles per hour) and lane count for each turn:")

    for turn in access_1_turns:
        volume = int(input(f"Traffic volume for {turn} from access 1: "))
        if turn == 'right':
            is_free = input("Is the right turn from access 1 free? (yes/no): ").strip().lower()
            if is_free == 'yes':
                volume = 0
                free_rights.append(True)
            else:
                free_rights.append(False)
        traffic_volume.append(volume)
        if volume != 0:
            lane_count = int(input(f"Enter the number of lanes for {turn}: "))
            lanes.append(lane_count)
        else:
            lanes.append(1)  # To avoid division by 0 later

    for turn in access_2_turns:
        volume = int(input(f"Traffic volume for {turn} from access 2: "))
        traffic_volume.append(volume)
        if volume != 0:
            lane_count = int(input(f"Enter the number of lanes for {turn}: "))
            lanes.append(lane_count)
        else:
            lanes.append(1)  # To avoid division by 0 later

    for turn in access_3_turns:
        volume = int(input(f"Traffic volume for {turn} from access 3: "))
        if turn == 'right':
            is_free = input("Is the right turn from access 3 free? (yes/no): ").strip().lower()
            if is_free == 'yes':
                volume = 0
                free_rights.append(True)
            else:
                free_rights.append(False)
        traffic_volume.append(volume)
        if volume != 0:
            lane_count = int(input(f"Enter the number of lanes for {turn}: "))
            lanes.append(lane_count)
        else:
            lanes.append(1)  # To avoid division by 0 later

    return traffic_volume, lanes, free_rights


# Function to calculate the adjusted volume for each turn
def calculate_adjusted_volumes(traffic_volume, lanes):
    adjusted_volumes = []
    for volume, lane_count in zip(traffic_volume, lanes):
        adjusted_volumes.append(volume / lane_count if lane_count != 0 else 0)
    return adjusted_volumes


# Function to calculate the determined values for each access
def calculate_determined_values(adjusted_volumes):
    access_1_volumes = adjusted_volumes[:2]
    access_2_volumes = adjusted_volumes[2:4]
    access_3_volumes = adjusted_volumes[4:]

    return access_1_volumes, access_2_volumes, access_3_volumes


# Function to calculate the total determined volume using both methods
def calculate_total_determined_volume(access_1_volumes, access_2_volumes, access_3_volumes, free_rights):
    # Accesses Method
    stage_1_accesses = max(access_1_volumes)
    stage_2_accesses = max(access_2_volumes)
    stage_3_accesses = max(access_3_volumes)
    total_determined_volume_accesses_method = stage_1_accesses + stage_2_accesses + stage_3_accesses

    # Isolated Lefts Method
    stage_1_isolated_lefts = max(access_1_volumes + [access_2_volumes[0]])
    stage_2_isolated_lefts = access_2_volumes[1]
    stage_3_isolated_lefts = max(access_3_volumes)
    total_determined_volume_isolated_lefts_method = stage_1_isolated_lefts + stage_2_isolated_lefts + stage_3_isolated_lefts

    total_determined_volume = min(total_determined_volume_accesses_method,
                                  total_determined_volume_isolated_lefts_method)
    method_used = "Accesses Method" if total_determined_volume == total_determined_volume_accesses_method else "Isolated Lefts Method"

    return total_determined_volume, method_used


# Function to calculate the capacity
def calculate_capacity(n, t):
    S = 1800  # Free flow (vehicles per hour per lane)
    C = 120  # Cycle length (seconds)
    k = n * t  # Lost time
    g = C - k  # Effective green time
    capacity = (S * g) / C
    return capacity


# Function to compute "C time"
def compute_C_time(total_determined_volume, r):
    C_time = (total_determined_volume / 3600) * r
    C_time = math.ceil(C_time / 5) * 5
    return C_time


# Function to perform the advanced check
def advanced_check(total_determined_volume, method_used, n, t):
    levels = {'C': 2.1, 'D': 1.9, 'E': 1.7}
    level_assigned = 'F'  # Default to Level F

    proceed_with_check = input("Would you like to proceed with the advanced check? (yes/no): ").strip().lower()
    if proceed_with_check != 'yes':
        return level_assigned  # Skip advanced check

    for level, r in levels.items():
        C_time = compute_C_time(total_determined_volume, r)
        if C_time > 120:
            continue

        # Calculate green time for each stage
        access_1_volumes, access_2_volumes, access_3_volumes = calculate_determined_values(adjusted_volumes)
        if method_used == "Accesses Method":
            stages = [access_1_volumes[0], access_2_volumes[0], access_3_volumes[0]]
        else:
            stages = [access_1_volumes[0], access_2_volumes[1], access_3_volumes[1]]

        green_times = [(stage * r * C_time) / 3600 for stage in stages]
        green_times = [math.ceil(gt) for gt in green_times]

        sum_g = sum(green_times) + (n * t)

        # Check criteria
        if sum_g <= C_time:
            level_assigned = level
            break

    return level_assigned


# Main function
def main():
    print("Welcome to the T Intersection Traffic Volume Determined Value Calculator!")

    # Ask the user for the intersection size
    intersection_size = int(input("Rate the intersection size (1 to 4, where 4 is the biggest): "))
    t_values = {1: 4, 2: 5, 3: 6, 4: 7}
    t = t_values.get(intersection_size, 6)  # Default to 6 if the user input is invalid

    traffic_volume, lanes, free_rights = get_traffic_volume_and_lanes()

    # Calculate adjusted volumes
    adjusted_volumes = calculate_adjusted_volumes(traffic_volume, lanes)
    print("Adjusted traffic volume data:", adjusted_volumes)

    # Calculate determined values for each access
    access_1_volumes, access_2_volumes, access_3_volumes = calculate_determined_values(adjusted_volumes)
    print("Determined values for each level:", [access_1_volumes, access_2_volumes, access_3_volumes])

    # Calculate total determined volume using both methods
    total_determined_volume, method_used = calculate_total_determined_volume(access_1_volumes, access_2_volumes,
                                                                             access_3_volumes, free_rights)
    print(f"Total determined volume: {total_determined_volume} using {method_used}")

    # Calculate capacity
    n = 3  # Number of stages
    capacity = calculate_capacity(n, t)
    print(f"Capacity: {capacity}")

    # Calculate and print the LOF check
    LOF_ratio = total_determined_volume / capacity
    print(f"LOF ratio: {LOF_ratio}")
    if LOF_ratio < 0.8:
        print("LOF=1, no need for advanced check.")
    else:
        print("LOF=2, there is a need for advanced check.")
        # Perform the advanced check
        level_of_service = advanced_check(total_determined_volume, method_used, n, t)
        print(f"Level of Service: {level_of_service}")


if __name__ == "__main__":
    main()
    
