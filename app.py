import streamlit as st
import math


def calculate_adjusted_volumes(traffic_volume, lanes):
    adjusted_volumes = []
    for volume, lane_count in zip(traffic_volume, lanes):
        adjusted_volumes.append(volume / lane_count if lane_count != 0 else 0)
    return adjusted_volumes


def calculate_determined_values(adjusted_volumes):
    access_1_volumes = adjusted_volumes[:2]
    access_2_volumes = adjusted_volumes[2:4]
    access_3_volumes = adjusted_volumes[4:]

    return access_1_volumes, access_2_volumes, access_3_volumes


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


def calculate_capacity(n, t):
    S = 1800  # Free flow (vehicles per hour per lane)
    C = 120  # Cycle length (seconds)
    k = n * t  # Lost time
    g = C - k  # Effective green time
    capacity = (S * g) / C
    return capacity


def calculate_c_time(total_determined_volume, r):
    c_time = math.ceil((total_determined_volume / 3600) * r / (1 - ((total_determined_volume / 3600) * r)))
    c_time = (c_time // 5) * 5  # Round up to the nearest multiple of 5
    return c_time


def calculate_g(stage_volume, r, c_time):
    g = math.ceil((stage_volume * r * c_time) / 3600)
    return g


def main():
    st.title("T Intersection Traffic Volume Determined Value Calculator")

    # User inputs
    intersection_size = st.slider("Rate the intersection size (1 to 4, where 4 is the biggest):", 1, 4, 3)
    t_values = {1: 4, 2: 5, 3: 6, 4: 7}
    t = t_values.get(intersection_size, 6)  # Default to 6 if the user input is invalid

    st.header("Enter Traffic Volume and Lane Count")

    traffic_volume = []
    lanes = []
    free_rights = []

    # Access 1
    st.subheader("Access 1")
    straight_1 = st.number_input("Traffic volume for straight from access 1:", 0)
    lanes_straight_1 = st.number_input("Enter the number of lanes for straight from access 1:", 1)
    right_1 = st.number_input("Traffic volume for right from access 1:", 0)
    right_free_1 = st.radio("Is the right turn from access 1 free?", ["yes", "no"])
    if right_free_1 == "yes":
        right_1 = 0
        free_rights.append(True)
    else:
        free_rights.append(False)
    lanes_right_1 = st.number_input("Enter the number of lanes for right from access 1:", 1)

    traffic_volume.extend([straight_1, right_1])
    lanes.extend([lanes_straight_1, lanes_right_1])

    # Access 2
    st.subheader("Access 2")
    straight_2 = st.number_input("Traffic volume for straight from access 2:", 0)
    lanes_straight_2 = st.number_input("Enter the number of lanes for straight from access 2:", 1)
    left_2 = st.number_input("Traffic volume for left from access 2:", 0)
    lanes_left_2 = st.number_input("Enter the number of lanes for left from access 2:", 1)

    traffic_volume.extend([straight_2, left_2])
    lanes.extend([lanes_straight_2, lanes_left_2])

    # Access 3
    st.subheader("Access 3")
    left_3 = st.number_input("Traffic volume for left from access 3:", 0)
    lanes_left_3 = st.number_input("Enter the number of lanes for left from access 3:", 1)
    right_3 = st.number_input("Traffic volume for right from access 3:", 0)
    right_free_3 = st.radio("Is the right turn from access 3 free?", ["yes", "no"])
    if right_free_3 == "yes":
        right_3 = 0
        free_rights.append(True)
    else:
        free_rights.append(False)
    lanes_right_3 = st.number_input("Enter the number of lanes for right from access 3:", 1)

    traffic_volume.extend([left_3, right_3])
    lanes.extend([lanes_left_3, lanes_right_3])

    # United Access 1
    if not free_rights[0]:  # Only ask if the right turn is not free
        united_1 = st.radio("Are the straight and right turns from access 1 united? (yes/no)", ["yes", "no"])
        if united_1 == "yes":
            # Calculate adjusted volume for access 1
            straight_1_new = (straight_1 + right_1) / (lanes_straight_1 + lanes_right_1 - 1)
            traffic_volume[0] = straight_1_new
            right_1 = 0  # Set right turn volume to zero

    # Calculate adjusted volumes
    adjusted_volumes = calculate_adjusted_volumes(traffic_volume, lanes)
    st.write("Adjusted traffic volume data:", adjusted_volumes)

    # Calculate determined values for each access
    access_1_volumes, access_2_volumes, access_3_volumes = calculate_determined_values(adjusted_volumes)
    st.write("Determined values for each level:", [access_1_volumes, access_2_volumes, access_3_volumes])

    # Calculate total determined volume using both methods
    total_determined_volume, method_used = calculate_total_determined_volume(access_1_volumes, access_2_volumes,
                                                                             access_3_volumes, free_rights)
    st.write(f"Total determined volume: {total_determined_volume} using {method_used}")

    # Calculate capacity
    n = 3  # Number of stages
    capacity = calculate_capacity(n, t)
    st.write(f"Capacity: {capacity}")

    # Calculate and print the LOF check
    LOF_ratio = total_determined_volume / capacity
    st.write(f"LOF ratio: {LOF_ratio}")
    if LOF_ratio < 0.8:
        st.write("LOF=1, no need for advanced check.")
    else:
        st.write("LOF=2, there is a need for advanced check.")
        proceed = st.radio("Do you want to proceed with the advanced check?", ["yes", "no"])
        if proceed == "yes":
            for level, r in zip(["C", "D", "E"], [2.1, 1.9, 1.7]):
                c_time = calculate_c_time(total_determined_volume, r)
                stage_volumes = [max(access_1_volumes), max(access_2_volumes),
                                 max(access_3_volumes)]  # Adjust according to method used
                gs = [calculate_g(volume, r, c_time) for volume in stage_volumes]
                if c_time <= 120 and sum(gs) + t <= c_time:
                    st.write(f"Level of Service: {level}")
                    break
            else:
                st.write("Level of Service: F")


if __name__ == "__main__":
    main()
