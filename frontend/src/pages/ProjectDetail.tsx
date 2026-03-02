import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import api from '../lib/api'

interface ProjectDetail {
  id: string
  title: string
  genre: string
  target_word_count: number
  current_word_count: number
}

export default function ProjectDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [project, setProject] = useState<ProjectDetail | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchProject()
  }, [id])

  const fetchProject = async () => {
    try {
      const response = await api.get(`/projects/${id}`)
      setProject(response.data)
    } catch (err) {
      console.error('Failed to fetch project:', err)
      navigate('/projects')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm('确定要删除这个项目吗?')) {
      return
    }

    try {
      await api.delete(`/projects/${id}`)
      navigate('/projects')
    } catch (err) {
      console.error('Failed to delete project:', err)
      alert('删除项目失败')
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
        <Link to="/projects" className="inline-block mb-6 text-gray-600 hover:text-gray-900">
          ← 返回项目列表
        </Link>

        {project && (
          <>
            <div className="mb-6">
              <div className="flex justify-between items-start">
                <div>
                  <h1 className="text-3xl font-bold mb-2">{project.title}</h1>
                  <div className="flex gap-4 text-gray-600">
                    <span>类型: {project.genre}</span>
                    <span>字数: {project.current_word_count.toLocaleString()}/{project.target_word_count.toLocaleString()}</span>
                  </div>
                </div>
                <button
                  onClick={handleDelete}
                  className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded"
                >
                  删除项目
                </button>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className={`h-3 rounded-full ${project.current_word_count >= project.target_word_count ? 'bg-green-500' : 'bg-blue-500'}`}
                  style={{
                    width: `${Math.min((project.current_word_count / project.target_word_count) * 100, 100)}%`
                  }}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Link to={`/projects/${id}/outline`} className="bg-blue-50 p-6 rounded-lg hover:bg-blue-100 transition-colors border-2 border-blue-200 hover:border-blue-300">
                <h3 className="font-semibold text-lg mb-2">📋 大纲</h3>
                <p className="text-gray-600">规划情节结构</p>
              </Link>

              <Link to={`/projects/${id}/characters`} className="bg-green-50 p-6 rounded-lg hover:bg-green-100 transition-colors border-2 border-green-200 hover:border-green-300">
                <h3 className="font-semibold text-lg mb-2">👥 角色</h3>
                <p className="text-gray-600">管理角色关系</p>
              </Link>

              <Link to={`/projects/${id}/chapters`} className="bg-purple-50 p-6 rounded-lg hover:bg-purple-100 transition-colors border-2 border-purple-200 hover:border-purple-300">
                <h3 className="font-semibold text-lg mb-2">📝 章节</h3>
                <p className="text-gray-600">撰写章节内容</p>
              </Link>

              <Link to={`/projects/${id}/viral-structure`} className="bg-yellow-50 p-6 rounded-lg hover:bg-yellow-100 transition-colors border-2 border-yellow-200 hover:border-yellow-300">
                <h3 className="font-semibold text-lg mb-2">🔥 爆款结构</h3>
                <p className="text-gray-600">应用成功模式</p>
              </Link>
            </div>

            <div className="mt-8 bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">快速开始</h2>
              <div className="space-y-3">
                <div className="flex items-start gap-3 p-4 bg-gray-50 rounded">
                  <span className="text-2xl">1️⃣</span>
                  <div>
                    <h4 className="font-semibold">选择爆款结构模板</h4>
                    <p className="text-gray-600 text-sm">根据小说类型选择合适的爆款结构</p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-4 bg-gray-50 rounded">
                  <span className="text-2xl">2️⃣</span>
                  <div>
                    <h4 className="font-semibold">创建角色和设定</h4>
                    <p className="text-gray-600 text-sm">定义主角、配角及其背景故事</p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-4 bg-gray-50 rounded">
                  <span className="text-2xl">3️⃣</span>
                  <div>
                    <h4 className="font-semibold">规划章节大纲</h4>
                    <p className="text-gray-600 text-sm">按照爆款结构规划故事情节</p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-4 bg-gray-50 rounded">
                  <span className="text-2xl">4️⃣</span>
                  <div>
                    <h4 className="font-semibold">开始创作</h4>
                    <p className="text-gray-600 text-sm">使用AI辅助创作章节内容</p>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
