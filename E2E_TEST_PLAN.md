# ORVENA End-to-End Testing Plan

## Test Environment
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- Test User: anagesh2410198@gmail.com
- Test Resume: D:\Main details\Anagesh_Resume.pdf

## Test Scenarios

### 1. Authentication Flow ✓
- [x] Sign up with new user
- [x] Login with existing user
- [x] Profile data loads correctly
- [x] Token persists across page refreshes

### 2. Career Discovery Module
**Test Objectives:**
- Verify 10 questions are asked and stored
- Test AI generation of recommendations
- Test fallback when AI fails
- Verify responses persist across sessions

**Test Steps:**
1. Navigate to /career/discovery
2. Answer all 10 questions with detailed responses
3. Complete session
4. Verify recommendations generated
5. Check if responses are saved in database
6. Test re-login - should not ask same questions again

### 3. Resume Intelligence Module
**Test Objectives:**
- Upload Anagesh_Resume.pdf
- Verify text extraction works
- Check 6-category scoring (both AI and fallback)
- Validate suggestions generation

**Test Steps:**
1. Navigate to /resume
2. Upload PDF: D:\Main details\Anagesh_Resume.pdf
3. Verify extraction completes
4. Check resume score (should show 6 categories)
5. Review AI suggestions
6. Test fallback scoring by simulating AI failure

**Expected Categories:**
- Contact Information
- Education
- Work Experience
- Skills
- Projects
- Overall Presentation

### 4. Job Recommender Module
**Test Objectives:**
- Generate job recommendations based on career results
- Input preferences (skills, location, salary)
- Verify job cards are clickable with links
- Test both AI and fallback matching

**Test Steps:**
1. Navigate to /jobs
2. Input preferences:
   - Skills: React, Python, AI/ML
   - Location: Remote/Bangalore
   - Expected Salary: ₹800,000 - ₹1,200,000
3. Get recommendations
4. Verify job cards have:
   - Company name
   - Job title
   - Location
   - Salary range
   - Clickable link to job posting
5. Test clicking on job cards

### 5. Career Roadmap Module
**Test Objectives:**
- Generate roadmap from career recommendations
- Verify visual timeline displays
- Check milestones are actionable
- Test both AI and fallback generation

**Test Steps:**
1. Navigate to /roadmap
2. Select target role from recommendations
3. Generate roadmap
4. Verify visual timeline shows:
   - Milestones with sequence
   - Estimated duration
   - Resources/links
   - Progress tracking
5. Test milestone completion

### 6. Progress Tracking Module
**Test Objectives:**
- Verify all completed activities show
- Check career results display
- Verify resume score displays
- Confirm roadmap progress shows

**Test Steps:**
1. Navigate to /progress
2. Verify displays:
   - Career discovery completion
   - Resume analysis score
   - Recommended jobs count
   - Roadmap milestones progress
3. Check all data is accurate

## Performance Tests

### Latency Targets
- Page load: < 2 seconds
- API response: < 3 seconds
- AI generation: < 10 seconds
- Fallback: < 2 seconds

### Test Checklist
- [ ] Career Discovery loads in < 2s
- [ ] Resume upload processes in < 5s
- [ ] Job recommendations load in < 3s
- [ ] Roadmap generation completes in < 8s
- [ ] Progress page loads in < 2s

## UI/UX Tests

### Hover Effects
- [ ] Dashboard cards lift on hover
- [ ] Job cards show hover effect
- [ ] Buttons have smooth transitions
- [ ] Cards have proper shadows

### Responsive Design
- [ ] Works on desktop (1920x1080)
- [ ] Works on tablet (768x1024)
- [ ] Works on mobile (375x667)

## Bug Tracking

### Known Issues to Fix
1. Profile shows "Alex Johnson" → Fixed ✓
2. Career questions asked repeatedly → Needs testing
3. Job cards not clickable → Need to add links
4. High latency → Need optimization
5. No hover effects → Fixed ✓

### New Issues Found
(Will be populated during testing)

## Test Results Summary
(To be completed after testing)

---

**Testing Date:** 2026-10-12
**Tester:** AI Agent
**Status:** In Progress
