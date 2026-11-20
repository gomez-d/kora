
import requests


def forward_request(
    method,
    url,
    headers=None,
    params=None,
    json=None,
    data=None,
):
    return requests.request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        json=json,
        data=data,
        timeout=180,
    )
