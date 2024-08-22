from datetime import datetime, timedelta
import random

class ElectricVehicle:
    def __init__(self, battery_capacity, consumption_city, consumption_highway, regen_efficiency, charging_speed, fast_charging_speed=None):
        self.battery_capacity = battery_capacity  # kWh
        self.consumption_city = consumption_city  # kWh/100km in city driving
        self.consumption_highway = consumption_highway  # kWh/100km on highway driving
        self.regen_efficiency = regen_efficiency  # %
        self.charging_speed = charging_speed  # kW (slow charging)
        self.fast_charging_speed = fast_charging_speed  # kW (fast charging), if available
        self.current_battery = battery_capacity  # kWh, starts with a full battery

    def distance_on_full_charge(self, driving_condition):
        if driving_condition == 'city':
            consumption = self.consumption_city
        elif driving_condition == 'highway':
            consumption = self.consumption_highway
        else:
            consumption = (self.consumption_city + self.consumption_highway) / 2

        distance = (self.battery_capacity / consumption) * 100
        return distance

    def recover_energy_braking(self, distance_traveled, speed):
        energy_used = (distance_traveled / 100) * self.average_consumption()
        if speed == 'low':
            regen_efficiency_actual = self.regen_efficiency * 0.7
        elif speed == 'high':
            regen_efficiency_actual = self.regen_efficiency * 1.2
        else:
            regen_efficiency_actual = self.regen_efficiency

        energy_recovered = energy_used * regen_efficiency_actual
        self.current_battery += energy_recovered
        if self.current_battery > self.battery_capacity:
            self.current_battery = self.battery_capacity  # Cap at full capacity
        return energy_recovered

    def average_consumption(self):
        return (self.consumption_city + self.consumption_highway) / 2

    def charge_time(self):
        if self.fast_charging_speed:
            fast_charge_capacity = self.battery_capacity * 0.8
            slow_charge_capacity = self.battery_capacity * 0.2

            fast_charge_time = fast_charge_capacity / self.fast_charging_speed
            slow_charge_time = slow_charge_capacity / self.charging_speed

            return fast_charge_time + slow_charge_time
        else:
            return self.battery_capacity / self.charging_speed

    def simulate_trip(self, distance_traveled, driving_condition, speed):
        if driving_condition == 'city':
            consumption_per_100km = self.consumption_city
        elif driving_condition == 'highway':
            consumption_per_100km = self.consumption_highway
        else:
            consumption_per_100km = self.average_consumption()

        energy_used = (distance_traveled / 100) * consumption_per_100km
        energy_recovered = self.recover_energy_braking(distance_traveled, speed=speed)

        net_energy_used = energy_used - energy_recovered
        self.current_battery -= net_energy_used

        if self.current_battery < 0:
            self.current_battery = 0  # Depleted battery
        return self.current_battery


class ChargingStation:
    def __init__(self, name, distance_from_vehicle):
        self.name = name
        self.distance_from_vehicle = distance_from_vehicle  # km
        self.current_time = datetime.now()
        self.slots = [self.current_time + timedelta(hours=i) for i in range(1, 25)]
        self.booked_slots = []

    def display_slots(self):
        print(f"\nAvailable charging slots at {self.name}:")
        for idx, slot in enumerate(self.slots):
            if slot not in self.booked_slots:
                print(f"{idx + 1}. {slot.strftime('%Y-%m-%d %H:%M')}")

    def book_slot(self, slot_number):
        if 1 <= slot_number <= len(self.slots):
            selected_slot = self.slots[slot_number - 1]
            if selected_slot not in self.booked_slots:
                self.booked_slots.append(selected_slot)
                print(f"Slot successfully booked at {self.name} for {selected_slot.strftime('%Y-%m-%d %H:%M')}.")
            else:
                print("This slot is already booked. Please choose another slot.")
        else:
            print("Invalid slot number. Please try again.")


class ChargingStationFinder:
    def __init__(self):
        self.stations = self.generate_stations()

    def generate_stations(self):
        # Randomly generate a few charging stations with distances
        return [
            ChargingStation("EV Station A", random.uniform(1, 10)),
            ChargingStation("EV Station B", random.uniform(5, 15)),
            ChargingStation("EV Station C", random.uniform(10, 20))
        ]

    def find_nearby_stations(self):
        print("\nNearby charging stations:")
        for idx, station in enumerate(self.stations):
            print(f"{idx + 1}. {station.name} - {station.distance_from_vehicle:.2f} km away")
        return self.stations


# Console Input Version of the Example Usage
def main():
    # Define vehicle specifications
    battery_capacity = 75  # kWh
    consumption_city = 17  # kWh/100km in city driving
    consumption_highway = 13  # kWh/100km on highway driving
    regen_efficiency = 0.30  # 30%
    charging_speed = 11  # kW (slow charging)
    fast_charging_speed = 50  # kW (fast charging, if available)

    # Instantiate the ElectricVehicle class
    ev = ElectricVehicle(battery_capacity, consumption_city, consumption_highway, regen_efficiency, charging_speed, fast_charging_speed)

    # Input distance for the trip
    distance = float(input("Enter the distance to be traveled (in km): "))

    # Input driving condition
    driving_condition = input("Enter the driving condition (city/highway/mixed): ").lower()
    while driving_condition not in ['city', 'highway', 'mixed']:
        print("Invalid input. Please enter 'city', 'highway', or 'mixed'.")
        driving_condition = input("Enter the driving condition (city/highway/mixed): ").lower()

    # Input speed condition
    speed = input("Enter the driving speed (low/moderate/high): ").lower()
    while speed not in ['low', 'moderate', 'high']:
        print("Invalid input. Please enter 'low', 'moderate', or 'high'.")
        speed = input("Enter the driving speed (low/moderate/high): ").lower()

    # Calculate distance on a full charge
    full_charge_distance = ev.distance_on_full_charge(driving_condition)
    print(f"\nDistance on a full charge ({driving_condition} driving): {full_charge_distance:.2f} km")

    # Simulate a trip with the input parameters
    battery_after_trip = ev.simulate_trip(distance, driving_condition, speed)
    print(f"Battery remaining after a {distance} km trip: {battery_after_trip:.2f} kWh")

    # Energy recovered during the trip
    energy_recovered = ev.recover_energy_braking(distance, speed)
    print(f"Energy recovered through regenerative braking: {energy_recovered:.2f} kWh")

    # Calculate charging time
    charge_time = ev.charge_time()
    print(f"Time to fully charge the vehicle with fast charging: {charge_time:.2f} hours")

    # Find nearby charging stations
    charging_finder = ChargingStationFinder()
    stations = charging_finder.find_nearby_stations()

    # Select a station and book a slot
    station_number = int(input("\nEnter the station number you want to book a slot at: "))
    if 1 <= station_number <= len(stations):
        selected_station = stations[station_number - 1]
        selected_station.display_slots()
        slot_number = int(input("\nEnter the slot number you want to book: "))
        selected_station.book_slot(slot_number)
    else:
        print("Invalid station number. Exiting.")


# Run the main function
if __name__ == "__main__":
    main()
