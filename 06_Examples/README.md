# SCRT Worked Encodings

These examples show how declared SCRT models instantiate the theory. They are mathematical modeling demonstrations; they do not certify any real deployment, infer evidence authenticity, or establish that a real architecture has been encoded completely.

## Recommended reading order

1. **[Shared Signing Root, Continued Operation, and Recovery Contention](./SCRT_Shared_Signing_Root_Recovery_Contention_Worked_Example_v2_18_0.md)**
   Practical bridge to the v2.18 phase theorem. Multiple services remain operational after a declared trust-root compromise, while individually valid certified recoveries compete for exclusive ceremony and approval resources. The example exposes the distinction between local recoverability and global assurance compatibility.

2. **[Realistic Supply-Chain Assurance Worked Example](./SCRT_Realistic_Supply_Chain_Assurance_Worked_Example_v2_18_0.md)**
   Maps `C_op`, `C_cert`, ancestry, evidence compromise, and recovery to a recognizable software-supply-chain setting. All independence relationships are explicit modeling assumptions.

3. **[Exclusive Recovery Resource Worked Example](./SCRT_Exclusive_Recovery_Resource_Worked_Example_v2_18_0.md)**
   Minimal example of the exclusive-resource phase: singleton local certified responses can be jointly incompatible.

## Compact structural examples

- **[Operational / Certified Divergence](./SCRT_Operational_Certified_Divergence_Example_v2_7_0.md)** — basic separation between operational and certified capacity.
- **[Evidence-Only Silent Assurance](./SCRT_Evidence_Only_Silent_Assurance_Example_v2_7_0.md)** — evidence compromise can reduce certified assurance without destroying operation.
- **[Campaign Residual Separation](./SCRT_Campaign_Residual_Example_v2_7_0.md)** — states equal under a current scalar view can be separated by admitted future campaign behavior.

## Modeling boundary

Every route, independence relation, compromise state, recovery action, resource claim, and target in these examples is part of the declared encoding. The examples illustrate consequences of those declarations; they do not establish that the declarations hold for any specific deployed system.

See the [Cyber Architecture Encoding Contract](../01_Theory/SCRT_Cyber_Architecture_Encoding_Contract_v2_18_0.md), [Threat Model and Assumption Boundary](../01_Theory/SCRT_Threat_Model_and_Assumption_Boundary_v2_18_0.md), and [Claim Boundary](../04_Research_Context/SCRT_Claim_Boundary_v2_18_0.md).
