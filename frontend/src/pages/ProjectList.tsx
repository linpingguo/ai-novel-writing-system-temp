import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../lib/api'

interface Project {
  id: string
  title: string
  genre: string
  target_word_count: number
  current_word_count: number
  created_at: string
}

export default function ProjectList() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newProjectTitle, setNewProjectTitle] = useState('')
  const [newProjectGenre, setNewProjectGenre] = useState('玄幻')
  const navigate = useNavigate()

  useEffect(() => {
    fetchProjects()
  }, [])

  const fetchProjects = async () => {
    try {
      const response = await api.get('/projects')
      setProjects(response.data || [])
    } catch (err) {
      console.error('Failed to fetch projects:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await api.post('/projects', {
        title: newProjectTitle,
        genre: newProjectGenre,
        target_word_count: 80000
      })
      setShowCreateModal(false)
      setNewProjectTitle('')
      fetchProjects()
    } catch (err: any) {
      console.error('Failed to create project:', err)
      alert('创建项目失败')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-600">加载中...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">我的项目</h1>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
          >
            + 创建新项目
          </button>
        </div>

        {projects.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📚</div>
            <h2 className="text-xl font-semibold text-gray-600 mb-2">还没有项目</h2>
            <p className="text-gray-500">点击上方按钮创建你的第一个小说项目</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {projects.map((project) => (
              <div
                key={project.id}
                onClick={() => navigate(`/projects/${project.id}`)}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer border border-gray-200 hover:border-blue-300"
              >
                <div className="flex justify-between items-start mb-4">
                  <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                    {project.genre}
                  </span>
                  <span className="text-gray-500 text-sm">
                    {new Date(project.created_at).toLocaleDateString()}
                  </span>
                </div>
                <h2 className="text-xl font-semibold mb-2">{project.title}</h2>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">目标字数:</span>
                    <span className="font-medium">{project.target_word_count.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">当前字数:</span>
                    <span className={`font-medium ${project.current_word_count >= project.target_word_count ? 'text-green-600' : 'text-blue-600'}`}>
                      {project.current_word_count.toLocaleString()}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                    <div
                      className={`h-2 rounded-full ${project.current_word_count >= project.target_word_count ? 'bg-green-500' : 'bg-blue-500'}`}
                      style={{
                        width: `${Math.min((project.current_word_count / project.target_word_count) * 100, 100)}%`
                      }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
              <h2 className="text-xl font-bold mb-4">创建新项目</h2>
              <form onSubmit={handleCreateProject} className="space-y-4">
                <div>
                  <label className="block mb-2 font-medium">项目标题</label>
                  <input
                    type="text"
                    value={newProjectTitle}
                    onChange={(e) => setNewProjectTitle(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500"
                    placeholder="请输入项目标题"
                    required
                  />
                </div>
                <div>
                  <label className="block mb-2 font-medium">小说类型</label>
                  <select
                    value={newProjectGenre}
                    onChange={(e) => setNewProjectGenre(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="玄幻">玄幻</option>
                    <option value="都市">都市</option>
                    <option value="言情">言情</option>
                    <option value="悬疑">悬疑</option>
                  </select>
                </div>
                <div className="flex gap-3">
                  <button
                    type="submit"
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg"
                  >
                    创建
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-700 font-bold py-3 px-4 rounded-lg"
                  >
                    取消
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
