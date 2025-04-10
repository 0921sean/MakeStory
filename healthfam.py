import os

# Data of people and their respective workout counts in the format (completed/total)
people_workout_counts = {
    '권정호': 1,
    # '김세호': ,
    '김현빈': 3,
    '성현우': 1,
    '신동훈': 2,
    '이명건': 1,
    '이승준': 3,
    '이준성': 3,
    '이형민': 1,
    '전은결': 3,
    '천승범': 2,
    '황동근': 3
}

# Initialize the penalty system
penalties = {}

# Apply fines based on workout counts
for person, workout_count in people_workout_counts.items():
    if workout_count >= 3 or workout_count == -1:  # Full workouts completed
        penalties[person] = 0
    else:
        penalties[person] = 15000 - 5000 * workout_count

workout_text = []
for person, num in people_workout_counts.items():
    if num == -1:
        workout_text.append(f"{person}: 0/0")
    else:
        workout_text.append(f"{person}: {num}/3")

for workout in workout_text:
    print(workout)
    
print("")
        
penalty_groups = {
    5000: [],
    10000: [],
    15000: []
}

for person, fine in penalties.items():
    if fine > 0:
        penalty_groups[fine].append(person)

# Generate the grouped penalty text
penalty_text = []

for fine in [5000, 10000, 15000]:
    if penalty_groups[fine]:
        names = [person[1:] for person in penalty_groups[fine]]
        if len(names) > 1:
            penalty_text.append(f"{' '.join(names)} {fine}원씩")
        else:
            penalty_text.append(f"{' '.join(names)} {fine}원")

# Join the penalty information into a single string
penalty_output = "벌금 " + " ".join(penalty_text)
print(penalty_output)

# Manage individual penalties in penalty_list.txt
penalty_file = "penalty_list.txt"
penalty_totals = {}

# Check if the file exists
if os.path.exists(penalty_file):
    # Read the current penalties from the file
    with open(penalty_file, "r") as file:
        for line in file:
            person, amount = line.strip().split(': ')
            penalty_totals[person] = int(amount.replace(',', '').replace('원', ''))
else:
    # Initialize an empty dictionary if the file doesn't exist
    penalty_totals = {}

# Update the individual penalties
for person, fine in penalties.items():
    if fine > 0:
        if person in penalty_totals:
            penalty_totals[person] += fine
        else:
            penalty_totals[person] = fine

# Write the updated totals back to penalty_list.txt
with open(penalty_file, "w") as file:
    for person, total_fine in penalty_totals.items():
        formatted_fine = f"{total_fine:,}원"
        file.write(f"{person}: {formatted_fine}\n")

# Define the file that will store the total penalty
total_penalty_file = "total_penalty.txt"

# Check if the file exists
if os.path.exists(total_penalty_file):
    # Read the current total penalty from the file
    with open(total_penalty_file, "r") as file:
        total_penalty = int(file.read().strip())
else:
    # Initialize total_penalty if the file doesn't exist
    total_penalty = 0

# Calculate the sum of the penalties for this round
current_total_penalty = sum([fine * len(penalty_groups[fine]) for fine in penalty_groups if fine > 0])

# Add the current total to the existing total
total_penalty += current_total_penalty

# Save the updated total penalty back to the file
with open(total_penalty_file, "w") as file:
    file.write(str(total_penalty))

# Format the total penalty as a number with commas for thousands
formatted_total_penalty = f"{total_penalty:,}원"

# Print the updated total penalty
print(f"총금액: {formatted_total_penalty}")