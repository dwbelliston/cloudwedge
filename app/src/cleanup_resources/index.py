"""
Wrap lambda handler and call main app
"""
import cfnresponse

from app import CleanupResources


def run_app(evt=None, ctx=None):
    """Parse event and run main app"""

    request_type = evt['RequestType']

    if request_type != 'Delete':
        # If its not delete, we dont need to do anything, just be done
        cfnresponse.send(
            evt, ctx, cfnresponse.SUCCESS, {}, "CleanupResourcesId")

    else:
        try:
            # Stack is deleting, go cleanup the things
            CleanupResources().run()

            cfnresponse.send(
                evt, ctx, cfnresponse.SUCCESS, {}, "CleanupResourcesId")

        except Exception as err:
            cfnresponse.send(
                evt, ctx, cfnresponse.FAILED, {}, "CleanupResourcesId")


def lambda_handler(event, context):
    """Lambda handler"""
    try:
        return run_app(event, context)
    except Exception as err:
        raise err
