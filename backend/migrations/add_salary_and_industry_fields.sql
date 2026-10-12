-- Migration: Add salary and industry trend fields to career_recommendations table
-- Created: 2026-10-12
-- Description: Adds salary range and industry trend information to career recommendations

-- Add salary fields
ALTER TABLE career_recommendations 
ADD COLUMN IF NOT EXISTS salary_range_min INTEGER,
ADD COLUMN IF NOT EXISTS salary_range_max INTEGER,
ADD COLUMN IF NOT EXISTS salary_currency VARCHAR(3) DEFAULT 'USD',
ADD COLUMN IF NOT EXISTS salary_period VARCHAR(20) DEFAULT 'annual',
ADD COLUMN IF NOT EXISTS industry_trend TEXT,
ADD COLUMN IF NOT EXISTS market_growth TEXT;

-- Add indexes for filtering by salary
CREATE INDEX IF NOT EXISTS idx_recommendations_salary_min 
ON career_recommendations(salary_range_min);

CREATE INDEX IF NOT EXISTS idx_recommendations_salary_max 
ON career_recommendations(salary_range_max);

-- Update existing records to have default salary info (if any exist)
UPDATE career_recommendations 
SET 
    salary_currency = 'USD',
    salary_period = 'annual'
WHERE salary_currency IS NULL OR salary_period IS NULL;

-- Add comment to table
COMMENT ON COLUMN career_recommendations.salary_range_min IS 'Minimum salary for the recommended role';
COMMENT ON COLUMN career_recommendations.salary_range_max IS 'Maximum salary for the recommended role';
COMMENT ON COLUMN career_recommendations.salary_currency IS 'Currency code (ISO 4217)';
COMMENT ON COLUMN career_recommendations.salary_period IS 'Salary period: annual or monthly';
COMMENT ON COLUMN career_recommendations.industry_trend IS 'Current industry trends for this career';
COMMENT ON COLUMN career_recommendations.market_growth IS 'Market growth outlook and statistics';
