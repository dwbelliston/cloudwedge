"""
Wrap lambda handler and call main app
"""

from app import IngestAlert


def run_app(evt=None, ctx=None):
    """Parse event and run main app"""

    resources = IngestAlert(event=evt).run()

    return resources


def lambda_handler(event, context):
    """Lambda handler"""
    try:
        return run_app(event, context)
    except Exception as err:
        raise err
