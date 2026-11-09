/* 外部脚本：为了启用 CSP 拦截 Netlify 徽章，内联脚本必须有外链 */
// 动态读取 updates/version.json，渲染版本 / 大小 / 更新说明 / 下载地址。
      // 读取失败时降级到 latest.apk，不影响下载。
      (function () {
        var FALLBACK_APK = 'https://ghfast.top/https://github.com/329zxz2016/329zxz2016.github.io/releases/download/v1.4.1/daoban-calendar-1.4.1.apk?v=2018';

        function byId(id) {
          return document.getElementById(id);
        }

        function formatSize(bytes) {
          var n = Number(bytes);
          if (!isFinite(n) || n <= 0) return '—';
          var mb = n / (1024 * 1024);
          return mb >= 100 ? mb.toFixed(0) + ' MB' : mb.toFixed(1) + ' MB';
        }

        function formatDate(iso) {
          var d = new Date(String(iso || ''));
          if (isNaN(d.getTime())) return '—';
          function pad(n) {
            return n < 10 ? '0' + n : String(n);
          }
          // 用 YYYY-MM-DD，窄屏下也不会把「日」挤到第二行
          return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
        }

        function renderNotes(text) {
          var box = byId('notes-box');
          var content = byId('notes-content');
          if (!box || !content) return;
          var parts = String(text || '')
            .split(/[；;\n]+/)
            .map(function (s) {
              return s.trim();
            })
            .filter(Boolean);
          if (!parts.length) return;
          content.replaceChildren();
          if (parts.length === 1) {
            var p = document.createElement('p');
            p.textContent = parts[0];
            content.appendChild(p);
          } else {
            var ul = document.createElement('ul');
            parts.forEach(function (part) {
              var li = document.createElement('li');
              li.textContent = part;
              ul.appendChild(li);
            });
            content.appendChild(ul);
          }
          box.hidden = false;
        }

        function render(manifest) {
          var m = manifest || {};
          var versionName = m.versionName ? String(m.versionName) : '';
          var versionLabel = versionName ? 'v' + versionName : '最新版';
          var versionEl = byId('version-name');
          if (versionEl) versionEl.textContent = versionLabel;

          var metaVersion = byId('meta-version');
          if (metaVersion) metaVersion.textContent = versionName || '—';
          var metaSize = byId('meta-size');
          if (metaSize) metaSize.textContent = formatSize(m.sizeBytes);
          var metaDate = byId('meta-date');
          if (metaDate) metaDate.textContent = formatDate(m.releasedAt);
          var footerVersion = byId('footer-version');
          if (footerVersion) footerVersion.textContent = versionLabel;

          renderNotes(m.notes);

          // apkUrl 支持三种写法：绝对 https 地址、以 / 开头的站内绝对路径、相对路径。
          // 相对路径用 new URL(..., location.href) 解析，站点换任何域名都能下载。
          var apkUrl = FALLBACK_APK;
          if (typeof m.apkUrl === 'string' && m.apkUrl.trim()) {
            try {
              apkUrl = new URL(m.apkUrl.trim(), window.location.href).toString();
            } catch (e) {
              apkUrl = FALLBACK_APK;
            }
          }
          var download = byId('download-btn');
          if (download) download.href = apkUrl;

          var shaNote = byId('sha-note');
          if (shaNote && m.sha256) {
            shaNote.textContent =
              '安装包 SHA-256：' + String(m.sha256).toUpperCase();
            shaNote.title = 'App 内更新会自动校验该值';
          }

          var status = byId('manifest-status');
          if (status) status.hidden = true;
        }

        function fail(error) {
          console.warn('[daoban] 读取 version.json 失败，降级到 latest.apk', error);
          var versionEl = byId('version-name');
          if (versionEl) versionEl.textContent = '最新版';
          var status = byId('manifest-status');
          if (status) {
            status.textContent = '暂时读不到更新清单，可先下载 latest.apk。';
            status.className = 'status-error';
          }
          var download = byId('download-btn');
          if (download) download.href = FALLBACK_APK;
        }

        fetch('updates/version.json?ts=' + Date.now(), { cache: 'no-store' })
          .then(function (res) {
            if (!res.ok) throw new Error('HTTP ' + res.status);
            return res.json();
          })
          .then(render)
          .catch(fail);
      })();
