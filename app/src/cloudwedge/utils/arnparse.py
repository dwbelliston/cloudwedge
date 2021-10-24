# Credit: https://github.com/PokaInc/arnparse

def empty_str_to_none(str_):
    if str_ == '':
        return None

    return str_


class MalformedArnError(Exception):
    def __init__(self, arn_str):
        self.arn_str = arn_str

    def __str__(self):
        return 'arn_str: {arn_str}'.format(arn_str=self.arn_str)


class Arn(object):
    def __init__(self, partition, service, region, account_id, resource_type, resource, resource_id):
        self.partition = partition
        self.service = service
        self.region = region
        self.account_id = account_id
        self.resource_type = resource_type
        self.resource = resource
        self.resource_id = resource_id


def arnparse(arn_str):
    """Parsne arn to attributes"""

    # arn:aws:ec2:us-west-2:ACCOUNTID:instance/i-07c281f74d763f868
    if not arn_str.startswith('arn:'):
        raise MalformedArnError(arn_str)

    # ['arn', 'aws', 'ec2', 'us-west-2', 'ACCOUNTID', 'instance/i-07c281f74d763f868']
    elements = arn_str.split(':', 5)
    service = elements[2] # ec2
    resource = elements[5] # instance/i-07c281f74d763f868

    if service in ['s3', 'sns', 'apigateway', 'execute-api']:
        resource_type = None
    else:
        resource_type, resource = _parse_resource(resource) # instance

    resource_id = resource.replace(f'{resource_type}/', '')

    return Arn(
        partition=elements[1],
        service=service,
        region=empty_str_to_none(elements[3]),
        account_id=empty_str_to_none(elements[4]),
        resource_type=resource_type,
        resource=resource,
        resource_id=resource_id
    )


def _parse_resource(resource):
    first_separator_index = -1
    for idx, c in enumerate(resource):
        if c in (':', '/'):
            first_separator_index = idx
            break

    if first_separator_index != -1:
        resource_type = resource[:first_separator_index]
        resource = resource[first_separator_index + 1:]
    else:
        resource_type = None

    return resource_type, resource
