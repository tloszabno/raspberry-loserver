from hamcrest.core.base_matcher import BaseMatcher


class IsSortedByTimestamp(BaseMatcher):
    def __init__(self):
        self.failing_pair = None

    def _matches(self, item):
        prev = None
        for element in item:
            if prev and element.timestamp < prev.timestamp:
                self.failing_pair = (prev, element)
                return False
            prev = element
        return True

    def describe_to(self, description):
        description.append_text('Given list is not ordered by timestamp') \
                   .append_text('Found unsorted elements:') \
                   .append_text(str(self.failing_pair))


def is_sorted_by_timestamp():
    return IsSortedByTimestamp()
