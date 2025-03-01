from ortools.sat.python import cp_model
from Version02.database import ScheduloDatabase

def schedule_timetable():
    # Retrieve data from the database
    db = ScheduloDatabase()
    subjects = [dict(row) for row in db.get_subjects()]
    teachers = [dict(row) for row in db.get_teachers()]
    teacher_subjects = [dict(row) for row in db.get_teacher_subjects()]
    venues = [dict(row) for row in db.get_venues()]
    db.close()

    # Build mapping: subject code -> candidate teacher codes
    subject_teacher_map = {}
    for ts in teacher_subjects:
        subj = ts["subject_code"]
        teacher = ts["teacher_code"]
        subject_teacher_map.setdefault(subj, []).append(teacher)

    # Mapping for teacher workload limits
    teacher_workload = {t["code"]: t["max_workload"] for t in teachers}

    # Scheduling parameters
    num_days = 5
    slots_per_day = 6
    total_slots = num_days * slots_per_day
    num_venues = len(venues)
    if num_venues == 0:
        print("No venues available for scheduling.")
        return None

    model = cp_model.CpModel()

    # Decision variables: for each required session of a subject, assign a time slot, venue, and teacher.
    session_vars = []  # list of tuples: (subject_code, session_index, slot_var, venue_var, teacher_var)
    for subj in subjects:
        code = subj["code"]
        num_sessions = subj["min_hours_per_week"]
        candidate_teachers = subject_teacher_map.get(code, [])
        if not candidate_teachers:
            print(f"No teacher assigned for subject {code}. Skipping scheduling for this subject.")
            continue
        # Map candidate teacher codes to indices (based on teachers list order)
        candidate_teacher_indices = []
        teacher_index_map = {t["code"]: idx for idx, t in enumerate(teachers)}
        for tcode in candidate_teachers:
            if tcode in teacher_index_map:
                candidate_teacher_indices.append(teacher_index_map[tcode])
        if not candidate_teacher_indices:
            print(f"No valid teacher found for subject {code}.")
            continue
        for s in range(num_sessions):
            slot_var = model.NewIntVar(0, total_slots - 1, f"{code}_slot_{s}")
            venue_var = model.NewIntVar(0, num_venues - 1, f"{code}_venue_{s}")
            teacher_var = model.NewIntVarFromDomain(
                cp_model.Domain.FromValues(candidate_teacher_indices),
                f"{code}_teacher_{s}"
            )
            session_vars.append((code, s, slot_var, venue_var, teacher_var))

    # Constraint: No two sessions may share the same venue at the same time.
    for i in range(len(session_vars)):
        for j in range(i + 1, len(session_vars)):
            _, _, slot_i, venue_i, _ = session_vars[i]
            _, _, slot_j, venue_j, _ = session_vars[j]
            same_slot = model.NewBoolVar(f"same_slot_{i}_{j}")
            model.Add(slot_i == slot_j).OnlyEnforceIf(same_slot)
            model.Add(slot_i != slot_j).OnlyEnforceIf(same_slot.Not())
            model.Add(venue_i != venue_j).OnlyEnforceIf(same_slot)

    # Constraint: A teacher cannot be in two sessions at the same time.
    for i in range(len(session_vars)):
        for j in range(i + 1, len(session_vars)):
            _, _, slot_i, _, teacher_i = session_vars[i]
            _, _, slot_j, _, teacher_j = session_vars[j]
            same_teacher = model.NewBoolVar(f"same_teacher_{i}_{j}")
            model.Add(teacher_i == teacher_j).OnlyEnforceIf(same_teacher)
            model.Add(teacher_i != teacher_j).OnlyEnforceIf(same_teacher.Not())
            same_time = model.NewBoolVar(f"same_time_{i}_{j}")
            model.Add(slot_i == slot_j).OnlyEnforceIf(same_time)
            model.Add(slot_i != slot_j).OnlyEnforceIf(same_time.Not())
            model.AddBoolOr([same_teacher.Not(), same_time.Not()])

    # Constraint: Respect teacher workload limits.
    teacher_session_indicators = {t_idx: [] for t_idx in range(len(teachers))}
    for (code, s_idx, slot_var, venue_var, teacher_var) in session_vars:
        for t_idx in range(len(teachers)):
            indicator = model.NewBoolVar(f"{code}_{s_idx}_is_teacher_{t_idx}")
            model.Add(teacher_var == t_idx).OnlyEnforceIf(indicator)
            model.Add(teacher_var != t_idx).OnlyEnforceIf(indicator.Not())
            teacher_session_indicators[t_idx].append(indicator)
    for t_idx, indicators in teacher_session_indicators.items():
        if indicators:
            max_work = teacher_workload.get(teachers[t_idx]["code"], total_slots)
            model.Add(sum(indicators) <= max_work)

    # Solve the scheduling model.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        schedule = []
        for (code, s_idx, slot_var, venue_var, teacher_var) in session_vars:
            slot = solver.Value(slot_var)
            day = slot // slots_per_day
            time_slot = slot % slots_per_day
            venue_index = solver.Value(venue_var)
            teacher_index = solver.Value(teacher_var)
            schedule.append({
                "subject": code,
                "session": s_idx,
                "day": day,
                "time_slot": time_slot,
                "venue": venues[venue_index]["name"],
                "teacher": teachers[teacher_index]["code"]
            })
        return schedule
    else:
        print("No feasible schedule found.")
        return None

if __name__ == "__main__":
    schedule = schedule_timetable()
    if schedule:
        print("Generated Schedule:")
        for session in schedule:
            print(session)
