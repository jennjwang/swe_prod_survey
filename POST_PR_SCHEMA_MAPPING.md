# Post-PR Database Schema Mapping

## Table: `post-PR`

### Column Mapping

#### NASA-TLX Questions (1-7 scale)

| Column Name  | Question                                                                   | Survey Key      |
| ------------ | -------------------------------------------------------------------------- | --------------- |
| `nasa_tlx_1` | How mentally demanding was the task?                                       | `mental_demand` |
| `nasa_tlx_2` | How hurried or rushed was the pace of the task?                            | `pace`          |
| `nasa_tlx_3` | How successful were you in accomplishing what you were asked to do?        | `success`       |
| `nasa_tlx_4` | How hard did you have to work to accomplish your level of performance?     | `effort`        |
| `nasa_tlx_5` | How frustrated, annoyed, or stressed did you feel while reviewing this PR? | `frustration`   |

#### Code Quality Questions (1-5 scale)

| Column Name      | Question                                                                             | Survey Key      |
| ---------------- | ------------------------------------------------------------------------------------ | --------------- |
| `code_quality_1` | This code is easy to read (readability)                                              | `readability`   |
| `code_quality_2` | This code's logic and structure are easy to understand (analyzability)               | `analyzability` |
| `code_quality_3` | This code would be easy to modify or extend (modifiability)                          | `modifiability` |
| `code_quality_4` | This code would be easy to test (testability)                                        | `testability`   |
| `code_quality_5` | This code would be stable when changes are made. (stability)                         | `stability`     |
| `code_quality_6` | This code performs as intended. (correctness)                                        | `correctness`   |
| `code_quality_7` | This code follows the repository's established standards and practices. (compliance) | `compliance`    |

#### AI Condition Questions (AI users only)

| Column Name               | Question                                                                          | Type               |
| ------------------------- | --------------------------------------------------------------------------------- | ------------------ |
| `ai_speed_multiplier`     | How much did AI decrease or increase the time it took you to complete this issue? | `double precision` |
| `ai_code_review_approach` | During this task, which best describes how you reviewed AI-generated code?        | `text`             |

#### Primary Key

| Column Name      | Type     | Description                         |
| ---------------- | -------- | ----------------------------------- |
| `participant_id` | `bigint` | Primary key, unique per participant |
| `issue_id`       | `bigint` | The issue ID                        |

## Data Flow

### AI Condition Page (Page 12)

1. Collects `ai_speed_multiplier` (0.1 to 10.0)
2. Collects `ai_code_review_approach` (text selection)
3. Saves to `post-PR` table with participant_id as key
4. Uses `upsert` to handle duplicate submissions

### Post-Issue Questions Page (Page 13)

1. Collects all NASA-TLX responses (5 questions, 1-7 scale)
2. Collects all Code Quality responses (7 questions, 1-5 scale)
3. Maps survey keys to numbered database columns
4. Saves to `post-PR` table with participant_id as key
5. Uses `upsert` to handle duplicate submissions
6. Marks `survey_completed = true` in `repo-issues` table

## Upsert Behavior

Both pages use `upsert(on_conflict='participant_id')`:

- **First submission**: Inserts new row
- **Subsequent submissions**: Updates existing row
- **Ensures**: One record per participant

## Session State Storage

Responses are stored in session state with descriptive keys:

```python
st.session_state['survey_responses']['post_issue'] = {
    'mental_demand': "4",
    'pace': "5 - Very high",
    'success': "6",
    # ...
}
```

These are then converted to numbered database columns when saving.
