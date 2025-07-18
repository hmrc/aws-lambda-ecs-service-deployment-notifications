import ecs_service_deployment_notifications.ecs as ecs
import pytest


class TestServiceArn:
    @pytest.mark.parametrize(
        "service_arn, expected_cluster_name",
        [
            (
                "arn:aws:ecs:us-west-2:111122223333:service/default/servicetest",
                "default",
            ),
            (
                "arn:aws:ecs:eu-west-2:111122223333:service/example/default",
                "example",
            ),
            (
                "arn:aws:ecs:eu-west-2:111122223333:service/testing/servicename",
                "testing",
            ),
        ],
    )
    def test_constructor_splits_cluster_name(
        self,
        service_arn: str,
        expected_cluster_name: str,
    ):
        split_service_arn = ecs.ServiceArn(service_arn)
        assert split_service_arn.cluster_name == expected_cluster_name

    @pytest.mark.parametrize(
        "service_arn, expected_service_name",
        [
            (
                "arn:aws:ecs:us-west-2:111122223333:service/default/servicetest",
                "servicetest",
            ),
            (
                "arn:aws:ecs:eu-west-2:111122223333:service/example/default",
                "default",
            ),
            (
                "arn:aws:ecs:eu-west-2:111122223333:service/testing/servicename",
                "servicename",
            ),
        ],
    )
    def test_constructor_splits_service_name(
        self,
        service_arn: str,
        expected_service_name: str,
    ):
        split_service_arn = ecs.ServiceArn(service_arn)
        assert split_service_arn.service_name == expected_service_name

    @pytest.mark.parametrize(
        "invalid_service_arn, expected_exception_message",
        [
            (
                "arn:aws:ecs:us-west-2:service/default/servicetest",
                "ARN missing section",
            ),
            (
                "arn:aws:ecs:us-west-2:111122223333:extra:service/default/servicetest",
                "ARN has too many sections",
            ),
            (
                "arn:aws:ecs:eu-west-2:111122223333:service/default",
                "ARN missing path section",
            ),
            (
                "arn:aws:ecs:eu-west-2:111122223333:service/default/servicetest/extra",
                "ARN has too many path sections",
            ),
            (
                "arn:aws:ecs:eu-west-2:111122223333:task/default/taskId",
                "ARN does not have service path",
            ),
        ],
    )
    def test_constructor_exception_on_invalid_arn(self, invalid_service_arn: str, expected_exception_message: str):
        with pytest.raises(ValueError) as exc:
            ecs.ServiceArn(invalid_service_arn)
        assert str(exc.value) == expected_exception_message
