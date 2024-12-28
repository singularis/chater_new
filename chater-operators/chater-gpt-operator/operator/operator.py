import kopf
import kubernetes
from kubernetes import client, config


@kopf.on.create("chater.example.com", "v1", "chatergpts")
def create_chater_gpt(spec, **kwargs):
    """
    This function is triggered when a new ChaterGpt custom resource is created.
    It will:
      1) Create (or verify) a Namespace.
      2) Create a Secret with openAIAPIKey and secretKey.
      3) Create a Deployment referencing the env variables.
    """
    namespace = spec.get("namespace")
    bootstrap_server = spec.get("bootstrapServer")
    model = spec.get("model")
    vision_model = spec.get("visionModel")
    openai_api_key_b64 = spec.get("openAIAPIKey")
    secret_key_b64 = spec.get("secretKey")

    config.load_incluster_config()

    api_client = client.ApiClient()
    core_api = client.CoreV1Api(api_client)
    apps_api = client.AppsV1Api(api_client)

    namespace_body = client.V1Namespace(metadata=client.V1ObjectMeta(name=namespace))
    try:
        core_api.create_namespace(namespace_body)
        kopf.info(
            objs=kwargs["body"],
            reason="Created",
            message=f"Created Namespace: {namespace}",
        )
    except kubernetes.client.exceptions.ApiException as e:
        if e.status == 409:
            # Already exists
            kopf.info(
                objs=kwargs["body"],
                reason="Exists",
                message=f"Namespace {namespace} already exists.",
            )
        else:
            raise

    secret_body = client.V1Secret(
        api_version="v1",
        kind="Secret",
        metadata=client.V1ObjectMeta(name="chater-gpt", namespace=namespace),
        data={"OPENAI_API_KEY": openai_api_key_b64, "SECRET_KEY": secret_key_b64},
    )

    try:
        core_api.create_namespaced_secret(namespace=namespace, body=secret_body)
        kopf.info(
            objs=kwargs["body"], reason="Created", message="Created Secret chater-gpt."
        )
    except kubernetes.client.exceptions.ApiException as e:
        if e.status == 409:
            core_api.patch_namespaced_secret(
                name="chater-gpt", namespace=namespace, body=secret_body
            )
            kopf.info(
                objs=kwargs["body"],
                reason="Patched",
                message="Patched existing Secret chater-gpt.",
            )
        else:
            raise

    container = client.V1Container(
        name="chater-gpt",
        image="singularis314/chater-gpt:0.3",
        image_pull_policy="Always",
        env=[
            client.V1EnvVar(
                name="OPENAI_API_KEY",
                value_from=client.V1EnvVarSource(
                    secret_key_ref=client.V1SecretKeySelector(
                        name="chater-gpt", key="OPENAI_API_KEY"
                    )
                ),
            ),
            client.V1EnvVar(
                name="SECRET_KEY",
                value_from=client.V1EnvVarSource(
                    secret_key_ref=client.V1SecretKeySelector(
                        name="chater-gpt", key="SECRET_KEY"
                    )
                ),
            ),
            client.V1EnvVar(name="BOOTSTRAP_SERVER", value=bootstrap_server),
            client.V1EnvVar(name="MODEL", value=model),
            client.V1EnvVar(name="VISION_MODEL", value=vision_model),
        ],
    )

    pod_template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(
            labels={"app": "chater-gpt"},
            annotations={"co.elastic.logs/enabled": "true"},
        ),
        spec=client.V1PodSpec(containers=[container]),
    )

    deployment_spec = client.V1DeploymentSpec(
        replicas=1,
        selector=client.V1LabelSelector(match_labels={"app": "chater-gpt"}),
        template=pod_template,
    )

    deployment_body = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name="chater-gpt", namespace=namespace),
        spec=deployment_spec,
    )

    try:
        apps_api.create_namespaced_deployment(namespace=namespace, body=deployment_body)
        kopf.info(
            objs=kwargs["body"],
            reason="Created",
            message="Created Deployment chater-gpt.",
        )
    except kubernetes.client.exceptions.ApiException as e:
        if e.status == 409:
            apps_api.patch_namespaced_deployment(
                name="chater-gpt", namespace=namespace, body=deployment_body
            )
            kopf.info(
                objs=kwargs["body"],
                reason="Patched",
                message="Patched existing Deployment chater-gpt.",
            )
        else:
            raise

    return {"message": "chater-gpt Operator handling complete"}
