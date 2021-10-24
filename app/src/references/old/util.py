def get_tag_value(tags, tagkey):
    return next((d['Value'] for (index, d) in enumerate(tags)
                 if d['Key'] == tagkey), None)


def parse_tag_value_list(tag_value, service):
    '''Parse tag values to list'''

    seperator = '/' if service == 'rds' else '|'

    if tag_value:
        values_list = tag_value.replace(' ', '').split(seperator)
        # Dedupe list with set, then return list
        return list(set(values_list))
    else:
        return []
