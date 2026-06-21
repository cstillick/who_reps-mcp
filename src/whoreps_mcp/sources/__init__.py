"""Data sources, each isolated behind a small module so they can be tested
against recorded fixtures rather than live APIs.

- ``census`` — address -> lat/lon + districts + OCD divisions (no key).
- ``federal`` — congress-legislators roster -> U.S. Senators + House member (no key).
- ``openstates`` — state legislators by point (free key).
- ``governors`` — vendored, slow-changing list.
"""
