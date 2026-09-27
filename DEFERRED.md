# Deferred Steps

## STEP 23-25: ISO / Install / Hardware Validation

**Status:** Deferred until platform feature-complete.

**Reason:** WSL2 environment (no KVM, no proper UEFI persistence) makes
QEMU-based OS install fragile. ISO build works (verified). Install-to-disk
can be attempted on real hardware or KVM-capable host later.

**Approach:** Develop platform in WSL → run via web GUI → package as ISO
when platform is feature-complete (Phase 7-13 of master roadmap).
