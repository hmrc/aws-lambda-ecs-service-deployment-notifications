class ServiceArn:
    def __init__(self, service_arn: str) -> None:
        arn_split = service_arn.split(":")
        if len(arn_split) < 6:
            raise ValueError("ARN missing section")
        elif len(arn_split) > 6:
            raise ValueError("ARN has too many sections")

        resource_path = arn_split[5]
        resource_split = resource_path.split("/")

        if len(resource_split) < 3:
            raise ValueError("ARN missing path section")
        elif len(resource_split) > 3:
            raise ValueError("ARN has too many path sections")

        if resource_split[0] != "service":
            raise ValueError("ARN does not have service path")

        self.cluster_name = resource_split[1]
        self.service_name = resource_split[2]
