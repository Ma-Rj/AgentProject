import './Sidebar.css'

export default function Sidebar({ conversations, activeId, onSelect, onNew, onDelete, user, onLogout, isOpen, onToggle }) {
  return (
    <aside className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
      {/* 顶部 - 新建对话 */}
      <div className="sidebar-top">
        <button className="new-chat-btn" onClick={onNew}>
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
            <path d="M9 3v12M3 9h12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
          </svg>
          <span>新建对话</span>
        </button>
      </div>

      {/* 对话列表 */}
      <nav className="sidebar-list">
        {conversations.length === 0 ? (
          <div className="sidebar-empty">暂无对话记录</div>
        ) : (
          conversations.map((conv) => (
            <div
              key={conv.id}
              className={`sidebar-item ${conv.id === activeId ? 'active' : ''}`}
              onClick={() => onSelect(conv.id)}
            >
              <svg className="sidebar-item-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M2 4a2 2 0 012-2h8a2 2 0 012 2v5a2 2 0 01-2 2H7l-3 3V11H4a2 2 0 01-2-2V4z" stroke="currentColor" strokeWidth="1.3" />
              </svg>
              <span className="sidebar-item-title">{conv.title}</span>
              <button
                className="sidebar-item-delete"
                onClick={(e) => { e.stopPropagation(); onDelete(conv.id) }}
                aria-label="删除对话"
              >
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M3.5 3.5L10.5 10.5M10.5 3.5L3.5 10.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                </svg>
              </button>
            </div>
          ))
        )}
      </nav>

      {/* 底部 - 用户信息 */}
      <div className="sidebar-bottom">
        <div className="sidebar-user">
          <div className="user-avatar">
            {user?.username?.[0]?.toUpperCase() || 'U'}
          </div>
          <div className="user-info">
            <span className="user-name">{user?.username}</span>
            <span className="user-city">{user?.city || '未设置城市'}</span>
          </div>
          <button className="logout-btn" onClick={onLogout} aria-label="退出登录">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M6 2h6a2 2 0 012 2v8a2 2 0 01-2 2H6M2 8h8M8 5l3 3-3 3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </div>
      </div>
    </aside>
  )
}
