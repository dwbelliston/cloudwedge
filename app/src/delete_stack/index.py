"""
Wrap lambda handler and call main app
"""

from app import DeleteStack


def run_app(evt=None, ctx=None):
    """Parse event and run main app"""

    # Get target account from event
    target_account_id = evt['targetAccountId']

    resources = DeleteStack(target_account_id=target_account_id, event=evt).run()

    return resources

def lambda_handler(event, context):
    """Lambda handler"""
    try:
        return run_app(event, context)
    except Exception as err:
        raise err
