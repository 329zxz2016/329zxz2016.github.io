/* 外部脚本：为了启用 CSP 拦截 Netlify 徽章，内联脚本必须有外链 */
// 支持从 App / 首页带 ?version=1.1.0 打开时自动填好版本号
      (function () {
        try {
          var version = new URLSearchParams(window.location.search).get('version');
          var input = document.getElementById('version-input');
          if (version && input) input.value = String(version).slice(0, 40);
        } catch (error) {
          /* 老浏览器忽略即可 */
        }
      })();
