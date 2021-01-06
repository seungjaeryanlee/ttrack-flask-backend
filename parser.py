LABEL_TO_DB_FILES = {
    "Activities of Daily Living": "activities_of_daily_living.txt",
    "Ignore": "ignore_tasks.txt",
    "Misc": "misc_tasks.txt",
    "Personal Development": "personal_development_tasks.txt",
    "Personal Enjoyment": "personal_enjoyment_tasks.txt",
    "School and Work": "school_and_work_tasks.txt",
    "Side Projects": "side_projects.txt",
    "Sleep": "sleep.txt",
    "Social Life": "social_life.txt",
}
LABEL_PRIORITIES = [
    "Unknown",
    "School and Work",
    "Side Projects",
    "Social Life",
    "Personal Development",
    "Activities of Daily Living",
    "Misc",
    "Personal Enjoyment",
    "Sleep",
    "Ignore",
]


class Classifier():
    def __init__(self):
        self.read_classifier_files()

    def read_classifier_files(self):
        """
        Populate self.task_to_label
        """
        self.task_to_label = {}
        for label, db_filename in LABEL_TO_DB_FILES.items():
            with open('ttrack-database/parser_rules/{}'.format(db_filename), 'r') as f:
                for line in f.readlines():
                    task = line.strip()
                    if not task or task[0] == '#':
                        continue
                    self.task_to_label[task] = label

    def classify_task(self, task):
        if task in self.task_to_label.keys():
            return self.task_to_label[task]
        else:
            return "Unknown"

    def classify_tasks(self, tasks):
        return [self.classify_task(task) for task in tasks]

    def classify_line(self, line):
        tasks = self.split_line_to_tasks(line)
        task_labels = self.classify_tasks(tasks)

        line_label = None
        for label in LABEL_PRIORITIES:
            if label in task_labels:
                line_label = label
                break
        
        if line_label is None: line_label = "Unknown"
        if line_label == "Ignore": line_label = "Misc"

        return line_label, task_labels

    def split_line_to_tasks(self, line):
        tasks = line.split(' / ')
        tasks = [task.strip() for task in tasks]

        return tasks


# From seungjaeryanlee/self-management
def get_raw_lines(filepath):
    with open(filepath, 'r') as f:
        raw_lines = f.readlines()
        raw_lines = [raw_line.strip() for raw_line in raw_lines]

    # NOTE: We don't remove first line here and do it in frontend
    return raw_lines


# From seungjaeryanlee/self-management
def get_duration_and_lines(raw_lines):
    is_pm = False
    duration_and_lines = []
    last_time_in_minutes = 0
    total_timezone_difference = 0
    for raw_line in raw_lines:
        if raw_line == '~':
            is_pm = True
            continue

        if raw_line[:15] == '#TIMEZONECHANGE':
            if raw_line == "#TIMEZONECHANGE KST -> CDT (-14:00)":
                timezone_difference = -14 * 60
            elif raw_line == "#TIMEZONECHANGE CDT -> CST (-1:00)":
                timezone_difference = -1 * 60
            elif raw_line == "#TIMEZONECHANGE CST -> KST (+15:00)":
                timezone_difference = 15 * 60
            else:
                raise Exception("This timezone change is not supported yet.")

            last_time_in_minutes += timezone_difference
            if last_time_in_minutes < 12 * 60:
                is_pm = False
            if last_time_in_minutes > 12 * 60:
                is_pm = True
            total_timezone_difference += timezone_difference
            continue

        time = raw_line[:5].strip()
        hour = int(time[:-2]) + int(is_pm) * 12
        minute = int(time[-2:])
        time_in_minutes = 60 * hour + minute
        duration_in_minutes = time_in_minutes - last_time_in_minutes

        line = raw_line[5:].strip()
        duration_and_lines.append((duration_in_minutes, line))

        last_time_in_minutes = time_in_minutes

    # Make sure they add up to 1440 minutes (1440m = 24h = 1d)
    sum_of_all_durations = sum([duration for duration, _ in duration_and_lines])
    assert sum_of_all_durations == 24 * 60 - total_timezone_difference

    return duration_and_lines


def get_info_dict(duration_and_lines):
    classifier = Classifier()
    info_dict = {
        "durations": [],
        "lines": [],
        "tasks": [],
        "line_labels": [],
        "task_labels": [],
    }
    for duration, line in duration_and_lines:
        tasks = classifier.split_line_to_tasks(line)
        line_label, task_labels = classifier.classify_line(line)
        info_dict["durations"].append(duration)
        info_dict["lines"].append(line)
        info_dict["tasks"].append(tasks)
        info_dict["line_labels"].append(line_label)
        info_dict["task_labels"].append(task_labels)

    return info_dict
