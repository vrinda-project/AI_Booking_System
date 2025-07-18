-- Add hospital_id column to departments table
ALTER TABLE departments ADD COLUMN IF NOT EXISTS hospital_id INTEGER;

-- Add hospital_id column to doctors table
ALTER TABLE doctors ADD COLUMN IF NOT EXISTS hospital_id INTEGER;