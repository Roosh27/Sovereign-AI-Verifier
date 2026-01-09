import pandas as pd
import numpy as np
import random

def generate_balanced_support_data(n_total=1000):
    """
    Generates a balanced dataset (50/50 split) for Social Support Eligibility.
    Target: 1 (Accept), 0 (Reject)
    """
    data = []
    count_1 = 0
    count_0 = 0
    target_per_class = n_total // 2

    # Categorical options
    emp_statuses = ['Employed', 'Unemployed', 'Retired', 'Student']
    marital_options = ['Single', 'Married', 'Divorced', 'Widowed']

    while (count_1 + count_0) < n_total:
        # --- 1. Generate Random Profile ---
        age = random.randint(18, 85)
        family_size = random.randint(1, 10)
        dependents = random.randint(0, family_size - 1)
        income = random.randint(2000, 45000)
        savings = random.randint(0, 1500000)
        property_val = random.choices([0, random.randint(200000, 3000000)], weights=[0.7, 0.3])[0]
        has_disability = random.choices([0, 1], weights=[0.85, 0.15])[0]
        med_severity = random.randint(0, 10)
        status = random.choice(emp_statuses)
        marital = random.choice(marital_options)

        # --- 2. Apply Rulebook Logic ---
        # Household threshold: 12,000 base + 3,000 per dependent
        threshold = 12000 + (dependents * 3000)
        
        # Primary check
        eligible = 0
        if (income < threshold) and (property_val < 1000000) and (age >= 21):
            eligible = 1
        
        # Override: Disability increases income threshold by 50%
        if has_disability == 1 and income < (threshold * 1.5) and property_val < 1200000:
            eligible = 1

        # --- 3. Balancing logic ---
        if eligible == 1 and count_1 < target_per_class:
            data.append([age, marital, family_size, dependents, income, savings, 
                         property_val, has_disability, med_severity, status, 1])
            count_1 += 1
        elif eligible == 0 and count_0 < target_per_class:
            data.append([age, marital, family_size, dependents, income, savings, 
                         property_val, has_disability, med_severity, status, 0])
            count_0 += 1

    # --- 4. Finalize DataFrame ---
    columns = [
        'age', 'marital_status', 'family_size', 'dependents', 'monthly_income', 
        'total_savings', 'property_value', 'has_disability', 'medical_severity', 
        'employment_status', 'label'
    ]
    df = pd.DataFrame(data, columns=columns)
    
    # Shuffle so the model doesn't see all 1s then all 0s
    return df.sample(frac=1).reset_index(drop=True)

# Run and save
df_balanced = generate_balanced_support_data(1000)
df_balanced.to_csv('training_data/balanced_social_support_data.csv', index=False)

print("Dataset Generation Complete!")
print(df_balanced['label'].value_counts())