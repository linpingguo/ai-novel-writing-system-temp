import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import api from '../lib/api'

interface Character {
  id: string
  project_id: string
  name: string
  age: number | null
  personality: string[] | null
  appearance: string | null
  background: string | null
  created_at: string
}

interface Relation {
  source_char_id: string
  target_char_id: string
  relation_type: string
  description: string
}

export default function CharacterManagement() {
  const { id: projectId } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [characters, setCharacters] = useState<Character[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showRelationModal, setShowRelationModal] = useState(false)
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(null)
  const [newCharacter, setNewCharacter] = useState({
    name: '',
    age: null,
    personality: [],
    appearance: '',
    background: ''
  })
  const [newRelation, setNewRelation] = useState({
    target_char_id: '',
    relation_type: 'friend',
    description: ''
  })

  useEffect(() => {
    fetchCharacters()
  }, [projectId])

  const fetchCharacters = async () => {
    try {
      const response = await api.get(`/projects/${projectId}/characters`)
      setCharacters(response.data || [])
    } catch (err) {
      console.error('Failed to fetch characters:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateCharacter = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await api.post(`/projects/${projectId}/characters`, newCharacter)
      setShowCreateModal(false)
      setNewCharacter({
        name: '',
        age: null,
        personality: [],
        appearance: '',
        background: ''
      })
      fetchCharacters()
    } catch (err: any) {
      console.error('Failed to create character:', err)
      alert('创建角色失败')
    }
  }

  const handleDeleteCharacter = async (charId: string) => {
    if (!confirm('确定要删除这个角色吗?')) {
      return
    }

    try {
      await api.delete(`/projects/${projectId}/characters/${charId}`)
      fetchCharacters()
    } catch (err) {
      console.error('Failed to delete character:', err)
      alert('删除角色失败')
    }
  }

  const handleCreateRelation = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedCharacter) return

    try {
      await api.post(`/projects/${projectId}/characters/${selectedCharacter.id}/relations`, newRelation)
      setShowRelationModal(false)
      setNewRelation({
        target_char_id: '',
        relation_type: 'friend',
        description: ''
      })
      fetchCharacters()
    } catch (err: any) {
      console.error('Failed to create relation:', err)
      alert('创建关系失败')
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
        <div className="flex items-center justify-between mb-6">
          <Link to={`/projects/${projectId}`} className="text-gray-600 hover:text-gray-900">
            ← 返回项目
          </Link>
          <h1 className="text-3xl font-bold">角色管理</h1>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
          >
            + 创建角色
          </button>
        </div>

        {characters.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">👥</div>
            <h2 className="text-xl font-semibold text-gray-600 mb-2">还没有角色</h2>
            <p className="text-gray-500">点击上方按钮创建第一个角色</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {characters.map((char) => (
              <div
                key={char.id}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                      {char.name.charAt(0)}
                    </div>
                    <div>
                      <h3 className="text-xl font-bold">{char.name}</h3>
                      {char.age && (
                        <p className="text-gray-600">年龄: {char.age}</p>
                      )}
                      {char.personality && char.personality.length > 0 && (
                        <div className="mt-2">
                          <h4 className="font-semibold text-gray-700">性格特征</h4>
                          <div className="flex flex-wrap gap-2">
                            {char.personality.map((trait) => (
                              <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                                {trait}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setSelectedCharacter(char)}
                      className="bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded text-sm"
                    >
                      关系
                    </button>
                    <button
                      onClick={() => navigate(`/projects/${projectId}/characters/${char.id}`)}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded text-sm"
                    >
                      编辑
                    </button>
                    <button
                      onClick={() => handleDeleteCharacter(char.id)}
                      className="bg-red-600 hover:bg-red-700 text-white px-3 py-2 rounded text-sm"
                    >
                      删除
                    </button>
                  </div>
                </div>

                {char.appearance && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <h4 className="font-semibold mb-2">外貌描述</h4>
                    <p className="text-gray-600">{char.appearance}</p>
                  </div>
                )}

                {char.background && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <h4 className="font-semibold mb-2">背景故事</h4>
                    <p className="text-gray-600">{char.background}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
              <h2 className="text-xl font-bold mb-4">创建新角色</h2>
              <form onSubmit={handleCreateCharacter} className="space-y-4">
                <div>
                  <label className="block mb-2 font-medium">角色名称</label>
                  <input
                    type="text"
                    value={newCharacter.name}
                    onChange={(e) => setNewCharacter({...newCharacter, name: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500"
                    placeholder="请输入角色名称"
                    required
                  />
                </div>
                <div>
                  <label className="block mb-2 font-medium">年龄</label>
                  <input
                    type="number"
                    value={newCharacter.age || ''}
                    onChange={(e) => setNewCharacter({...newCharacter, age: e.target.value ? parseInt(e.target.value) : null})}
                    className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500"
                    placeholder="请输入年龄"
                  />
                </div>
                <div>
                  <label className="block mb-2 font-medium">性格特征</label>
                  <input
                    type="text"
                    value={newCharacter.personality.join(', ')}
                    onChange={(e) => setNewCharacter({...newCharacter, personality: e.target.value.split(',').map(s => s.trim())})}
                    className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500"
                    placeholder="例如: 勇敢,善良,固执"
                  />
                </div>
                <div>
                  <label className="block mb-2 font-medium">外貌描述</label>
                  <textarea
                    value={newCharacter.appearance}
                    onChange={(e) => setNewCharacter({...newCharacter, appearance: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500"
                    rows={3}
                    placeholder="描述角色的外貌特征"
                  />
                </div>
                <div>
                  <label className="block mb-2 font-medium">背景故事</label>
                  <textarea
                    value={newCharacter.background}
                    onChange={(e) => setNewCharacter({...newCharacter, background: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500"
                    rows={4}
                    placeholder="描述角色的背景和经历"
                  />
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

        {showRelationModal && selectedCharacter && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
              <h2 className="text-xl font-bold mb-4">添加角色关系</h2>
              <p className="text-gray-600 mb-2">为 <strong>{selectedCharacter.name}</strong> 添加关系</p>
              <form onSubmit={handleCreateRelation} className="space-y-4">
                <div>
                  <label className="block mb-2 font-medium">目标角色</label>
                  <select
                    value={newRelation.target_char_id}
                    onChange={(e) => setNewRelation({...newRelation, target_char_id: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    {characters.filter(c => c.id !== selectedCharacter.id).map((char) => (
                      <option key={char.id} value={char.id}>{char.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block mb-2 font-medium">关系类型</label>
                  <select
                    value={newRelation.relation_type}
                    onChange={(e) => setNewRelation({...newRelation, relation_type: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="friend">朋友</option>
                    <option value="enemy">敌人</option>
                    <option value="lover">恋人</option>
                    <option value="family">家人</option>
                  </select>
                </div>
                <div>
                  <label className="block mb-2 font-medium">关系描述</label>
                  <textarea
                    value={newRelation.description}
                    onChange={(e) => setNewRelation({...newRelation, description: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500"
                    rows={3}
                    placeholder="描述两个角色之间的关系"
                  />
                </div>
                <div className="flex gap-3">
                  <button
                    type="submit"
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg"
                  >
                    添加
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowRelationModal(false)}
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
