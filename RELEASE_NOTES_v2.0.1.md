# 🔧 git-batch-pull v2.0.1 - Packaging Fix Release

This is a quick patch release to fix a critical packaging issue discovered in v2.0.0 that prevented the security module from being properly included in the distributed package.

## 🐛 Bug Fixes

### Critical Packaging Fix
- **🔧 Fixed missing `token_manager.py` in package**: The security module's `token_manager.py` was inadvertently excluded from the built wheel due to an overly broad `.gitignore` pattern
- **📦 Package integrity restored**: All security components are now properly included in the distribution
- **🛡️ Security functionality preserved**: Interactive authentication and token management features work correctly

### Technical Details
- **Root Cause**: The `.gitignore` pattern `**/token*` was too broad and excluded the legitimate `token_manager.py` file
- **Solution**: Updated `.gitignore` to use a more specific pattern `**/token_*` that only excludes temporary token files
- **Validation**: Rebuilt package and confirmed `token_manager.py` is now included in the wheel distribution

### Test Coverage Improvements
- **🧪 Enhanced test robustness**: Improved test utilities and formatting for better maintainability
- **✅ Full test suite validation**: All 101 tests pass successfully after the fix
- **🔍 Health check verified**: CLI health check confirms all components are working correctly

## 🚀 What's Fixed

### For Users
- **✅ Security features work properly**: Interactive authentication and token management now function as intended
- **✅ Complete functionality**: All advertised features in v2.0.0 are now fully operational
- **✅ No configuration changes needed**: Existing v2.0.0 configurations remain valid

### For Developers
- **✅ Reliable builds**: Package building now includes all necessary modules
- **✅ Improved git tracking**: Better `.gitignore` patterns prevent similar issues in the future
- **✅ Enhanced testing**: More robust test utilities for continued development

## 📊 Release Metrics

- **Tests**: 101 passing, 4 skipped ✅
- **Coverage**: Security module fully included 📦
- **Build size**: No significant change from v2.0.0
- **Dependencies**: No changes to dependencies

## 🔄 Upgrade Instructions

### From v2.0.0
```bash
# Simple upgrade - no configuration changes needed
pip install --upgrade git-batch-pull==2.0.1
# or with pipx
pipx upgrade git-batch-pull
```

### Verification
```bash
# Verify the fix worked
git-batch-pull health
# Should show all green checks including security module
```

## 📝 Full v2.0.0 Feature Set Now Available

This patch ensures that all the powerful features introduced in v2.0.0 are fully functional:
- 🔐 Interactive HTTPS authentication
- 🛡️ Secure token management
- 🔄 Protocol switching capabilities
- 🏥 Comprehensive health checks
- ⚡ Performance optimizations
- 📦 Advanced repository management

## 🙏 Thanks

Thank you to users who reported the missing security module issue. This quick fix ensures the complete v2.0.0 experience is delivered as intended.

---

**Recommended Action**: All v2.0.0 users should upgrade to v2.0.1 to ensure full functionality.
