// @ts-nocheck
import { useState } from 'react';
import api from '../../lib/api';
import { useBuildings, useApartments, useCreateBuilding, useCreateApartment, useUpdateApartment, useUsers } from '../../hooks/useQueries';

function ApartmentRow({ apt, users, buildingId }: { apt: any; users: any[]; buildingId: string }) {
  const [editing, setEditing] = useState(false);
  const [ownerId, setOwnerId] = useState(apt.owner_id || '');
  const [tenantId, setTenantId] = useState(apt.tenant_id || '');
  const updateApartment = useUpdateApartment();

  const handleSave = async () => {
    await updateApartment.mutateAsync({
      apartmentId: apt.id,
      buildingId,
      owner_id: ownerId || null,
      tenant_id: tenantId || null,
    });
    setEditing(false);
  };

  const ownerName = users.find(u => u.id === apt.owner_id);
  const tenantName = users.find(u => u.id === apt.tenant_id);

  return (
    <li className="px-4 py-3 border-b border-gray-100 last:border-0">
      <div className="flex items-center justify-between">
        <div>
          <span className="font-medium text-sm text-gray-900">Unit {apt.unit_number}</span>
          {apt.floor !== null && apt.floor !== undefined && (
            <span className="ml-2 text-xs text-gray-500">Floor {apt.floor}</span>
          )}
          {apt.description && (
            <span className="ml-2 text-xs text-gray-400">{apt.description}</span>
          )}
        </div>
        <button onClick={() => setEditing(!editing)}
          className="text-xs text-blue-600 hover:text-blue-800">
          {editing ? 'Cancel' : 'Assign Users'}
        </button>
      </div>
      <div className="mt-1 text-xs text-gray-500 space-x-3">
        <span>Owner: <span className="text-gray-700">{ownerName ? `${ownerName.first_name} ${ownerName.last_name}` : '—'}</span></span>
        <span>Tenant: <span className="text-gray-700">{tenantName ? `${tenantName.first_name} ${tenantName.last_name}` : '—'}</span></span>
      </div>
      {editing && (
        <div className="mt-2 grid grid-cols-2 gap-2">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Owner</label>
            <select value={ownerId} onChange={e => setOwnerId(e.target.value)}
              className="w-full border border-gray-300 rounded px-2 py-1 text-xs">
              <option value="">— None —</option>
              {users.filter(u => u.role === 'owner' || u.role === 'manager').map(u => (
                <option key={u.id} value={u.id}>{u.first_name} {u.last_name} ({u.email})</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Tenant</label>
            <select value={tenantId} onChange={e => setTenantId(e.target.value)}
              className="w-full border border-gray-300 rounded px-2 py-1 text-xs">
              <option value="">— None —</option>
              {users.filter(u => u.role === 'tenant' || u.role === 'owner').map(u => (
                <option key={u.id} value={u.id}>{u.first_name} {u.last_name} ({u.email})</option>
              ))}
            </select>
          </div>
          <div className="col-span-2 flex justify-end">
            <button onClick={handleSave} disabled={updateApartment.isPending}
              className="px-3 py-1 bg-blue-600 text-white rounded text-xs hover:bg-blue-700 disabled:opacity-50">
              {updateApartment.isPending ? 'Saving...' : 'Save Assignment'}
            </button>
          </div>
        </div>
      )}
    </li>
  );
}

function BuildingCard({ building, users }: { building: any; users: any[] }) {
  const [expanded, setExpanded] = useState(false);
  const [showAddApt, setShowAddApt] = useState(false);
  const [aptForm, setAptForm] = useState({ unit_number: '', floor: '', description: '' });
  const { data: apartments = [], isLoading } = useApartments(expanded ? building.id : null);
  const createApartment = useCreateApartment();
  const [aptError, setAptError] = useState('');

  const handleAddApartment = async (e: any) => {
    e.preventDefault();
    setAptError('');
    try {
      await createApartment.mutateAsync({
        building_id: building.id,
        unit_number: aptForm.unit_number,
        floor: aptForm.floor ? parseInt(aptForm.floor) : undefined,
        description: aptForm.description || undefined,
      });
      setAptForm({ unit_number: '', floor: '', description: '' });
      setShowAddApt(false);
    } catch (err: any) {
      setAptError(err?.response?.data?.detail || 'Failed to add apartment');
    }
  };

  return (
    <div className="bg-white shadow rounded-lg mb-4">
      <div className="px-6 py-4 flex items-center justify-between cursor-pointer"
        onClick={() => setExpanded(!expanded)}>
        <div>
          <h3 className="text-base font-semibold text-gray-900">{building.name}</h3>
          <p className="text-sm text-gray-500">{building.address}, {building.city}</p>
          {building.country && <p className="text-xs text-gray-400">{building.country}</p>}
        </div>
        <span className="text-gray-400 text-lg">{expanded ? '▲' : '▼'}</span>
      </div>

      {expanded && (
        <div className="border-t border-gray-100">
          <div className="px-6 py-3 flex items-center justify-between bg-gray-50">
            <span className="text-sm font-medium text-gray-700">
              Apartments {isLoading ? '(loading...)' : `(${apartments.length})`}
            </span>
            <button onClick={(e) => { e.stopPropagation(); setShowAddApt(!showAddApt); }}
              className="text-xs text-blue-600 hover:text-blue-800 font-medium">
              + Add Apartment
            </button>
          </div>

          {showAddApt && (
            <form onSubmit={handleAddApartment} className="px-6 py-3 bg-blue-50 border-b border-blue-100">
              {aptError && <p className="text-xs text-red-600 mb-2">{aptError}</p>}
              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="block text-xs font-medium text-gray-600">Unit Number *</label>
                  <input required value={aptForm.unit_number}
                    onChange={e => setAptForm({...aptForm, unit_number: e.target.value})}
                    placeholder="e.g. 2A"
                    className="mt-1 w-full border border-gray-300 rounded px-2 py-1 text-xs"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600">Floor</label>
                  <input type="number" value={aptForm.floor}
                    onChange={e => setAptForm({...aptForm, floor: e.target.value})}
                    placeholder="e.g. 2"
                    className="mt-1 w-full border border-gray-300 rounded px-2 py-1 text-xs"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600">Description</label>
                  <input value={aptForm.description}
                    onChange={e => setAptForm({...aptForm, description: e.target.value})}
                    placeholder="e.g. 2-bed flat"
                    className="mt-1 w-full border border-gray-300 rounded px-2 py-1 text-xs"
                  />
                </div>
              </div>
              <div className="mt-2 flex justify-end space-x-2">
                <button type="button" onClick={() => setShowAddApt(false)}
                  className="px-3 py-1 text-xs border border-gray-300 rounded text-gray-700 hover:bg-gray-50">Cancel</button>
                <button type="submit" disabled={createApartment.isPending}
                  className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50">
                  {createApartment.isPending ? 'Adding...' : 'Add'}
                </button>
              </div>
            </form>
          )}

          <ul>
            {apartments.length === 0 && !isLoading ? (
              <li className="px-6 py-4 text-sm text-gray-500 text-center">No apartments yet. Add one above.</li>
            ) : (
              apartments.map((apt: any) => (
                <ApartmentRow key={apt.id} apt={apt} users={users} buildingId={building.id} />
              ))
            )}
          </ul>
        </div>
      )}
    </div>
  );
}

export function BuildingsTab() {
  const { data: buildings = [], isLoading, error } = useBuildings();
  const { data: usersData } = useUsers();
  const users = usersData?.items || [];
  const createBuilding = useCreateBuilding();
  const [showAdd, setShowAdd] = useState(false);
  const [addError, setAddError] = useState('');
  const [form, setForm] = useState({
    name: '', address: '', city: '', country: '', description: ''
  });

  const handleAdd = async (e: any) => {
    e.preventDefault();
    setAddError('');
    try {
      await createBuilding.mutateAsync(form);
      setForm({ name: '', address: '', city: '', country: '', description: '' });
      setShowAdd(false);
    } catch (err: any) {
      setAddError(err?.response?.data?.detail || 'Failed to create building');
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-md bg-red-50 p-4">
        <h3 className="text-sm font-medium text-red-800">Error loading buildings</h3>
        <p className="text-xs text-red-600 mt-1">Check that the backend is running and CORS is configured.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium text-gray-900">Buildings ({buildings.length})</h3>
        <button onClick={() => setShowAdd(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700">
          + Add Building
        </button>
      </div>

      {showAdd && (
        <div className="mb-6 bg-white shadow rounded-lg p-6">
          <h4 className="text-md font-medium text-gray-900 mb-4">Add New Building</h4>
          {addError && <p className="text-sm text-red-600 mb-3">{addError}</p>}
          <form onSubmit={handleAdd} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700">Building Name *</label>
              <input required value={form.name} onChange={e => setForm({...form, name: e.target.value})}
                placeholder="e.g. Sunset Apartments"
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Address *</label>
              <input required value={form.address} onChange={e => setForm({...form, address: e.target.value})}
                placeholder="e.g. 123 Main Street"
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">City *</label>
              <input required value={form.city} onChange={e => setForm({...form, city: e.target.value})}
                placeholder="e.g. Budapest"
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Country</label>
              <input value={form.country} onChange={e => setForm({...form, country: e.target.value})}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Description</label>
              <input value={form.description} onChange={e => setForm({...form, description: e.target.value})}
                placeholder="Optional description"
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm" />
            </div>
            <div className="sm:col-span-2 flex justify-end space-x-3">
              <button type="button" onClick={() => setShowAdd(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm text-gray-700 hover:bg-gray-50">Cancel</button>
              <button type="submit" disabled={createBuilding.isPending}
                className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700 disabled:opacity-50">
                {createBuilding.isPending ? 'Creating...' : 'Create Building'}
              </button>
            </div>
          </form>
        </div>
      )}

      {buildings.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg">No buildings yet.</p>
          <p className="text-sm mt-1">Add your first building using the button above.</p>
        </div>
      ) : (
        buildings.map((building: any) => (
          <BuildingCard key={building.id} building={building} users={users} />
        ))
      )}

      <div className="mt-6 p-4 bg-blue-50 rounded-lg text-sm text-blue-800">
        <strong>How user-building association works:</strong>
        <ul className="mt-1 list-disc list-inside space-y-1 text-xs">
          <li>Each <strong>apartment</strong> belongs to a building</li>
          <li>Each apartment can have one <strong>Owner</strong> and one <strong>Tenant</strong></li>
          <li>Click ▼ on a building to see its apartments and assign users</li>
          <li>Owners and tenants can then submit reports for their apartment</li>
        </ul>
      </div>
    </div>
  );
}

export default BuildingsTab;
