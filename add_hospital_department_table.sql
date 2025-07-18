-- Create hospital_department table for many-to-many relationship
CREATE TABLE IF NOT EXISTS hospital_department (
    hospital_id INTEGER NOT NULL,
    department_id INTEGER NOT NULL,
    PRIMARY KEY (hospital_id, department_id),
    FOREIGN KEY (hospital_id) REFERENCES hospitals (id),
    FOREIGN KEY (department_id) REFERENCES departments (id)
);