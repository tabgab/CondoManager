import { useState, useCallback } from 'react';
import type { Building, Apartment, ReportCreate, ReportPriority } from '../../types';

interface ReportFormProps {
  buildings: Building[];
  apartments: Apartment[];
  onSuccess: () => void;
  isSubmitting?: boolean;
}

type ReportCategory = 'maintenance' | 'cleaning' | 'safety' | 'noise' | 'other';

const categories: { value: ReportCategory; label: string }[] = [
  { value: 'maintenance', label: 'Maintenance' },
  { value: 'cleaning', label: 'Cleaning' },
  { value: 'safety', label: 'Safety' },
  { value: 'noise', label: 'Noise' },
  { value: 'other', label: 'Other' },
];

const priorities: { value: ReportPriority; label: string }[] = [
  { value: 'low', label: 'Low' },
  { value: 'normal', label: 'Medium' },
  { value: 'high', label: 'High' },
  { value: 'urgent', label: 'Urgent' },
];

export function ReportForm({ buildings, apartments, onSuccess, isSubmitting = false }: ReportFormProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState<ReportCategory | ''>('');
  const [priority, setPriority] = useState<ReportPriority>('normal');
  const [buildingId, setBuildingId] = useState<string>('');
  const [apartmentId, setApartmentId] = useState<string>('');
  const [photos, setPhotos] = useState<File[]>([]);

  const availableApartments = apartments.filter(a => a.building_id === buildingId);

  const isValid = title.trim() && description.trim() && category && buildingId;

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValid || isSubmitting) return;

    const reportData: ReportCreate & { category: string } = {
      title: title.trim(),
      description: description.trim(),
      priority,
      building_id: buildingId,
      apartment_id: apartmentId || undefined,
      category,
    };

    // TODO: Call API to submit report
    console.log('Submitting report:', reportData);
    console.log('Photos:', photos);

    // Reset form
    setTitle('');
    setDescription('');
    setCategory('');
    setPriority('normal');
    setBuildingId('');
    setApartmentId('');
    setPhotos([]);

    onSuccess();
  }, [isValid, isSubmitting, title, description, category, priority, buildingId, apartmentId, photos, onSuccess]);

  const handlePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setPhotos(Array.from(e.target.files));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 max-w-2xl">
      {/* Title */}
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700">
          Title <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Brief description of the issue"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          required
        />
      </div>

      {/* Category */}
      <div>
        <label htmlFor="category" className="block text-sm font-medium text-gray-700">
          Category <span className="text-red-500">*</span>
        </label>
        <select
          id="category"
          value={category}
          onChange={(e) => setCategory(e.target.value as ReportCategory)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          required
        >
          <option value="">Select a category</option>
          {categories.map((cat) => (
            <option key={cat.value} value={cat.value}>
              {cat.label}
            </option>
          ))}
        </select>
      </div>

      {/* Priority */}
      <div>
        <label htmlFor="priority" className="block text-sm font-medium text-gray-700">
          Priority
        </label>
        <select
          id="priority"
          value={priority}
          onChange={(e) => setPriority(e.target.value as ReportPriority)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
        >
          {priorities.map((p) => (
            <option key={p.value} value={p.value}>
              {p.label}
            </option>
          ))}
        </select>
      </div>

      {/* Building */}
      <div>
        <label htmlFor="building" className="block text-sm font-medium text-gray-700">
          Building <span className="text-red-500">*</span>
        </label>
        <select
          id="building"
          value={buildingId}
          onChange={(e) => {
            setBuildingId(e.target.value);
            setApartmentId('');
          }}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          required
        >
          <option value="">Select a building</option>
          {buildings.map((b) => (
            <option key={b.id} value={b.id}>
              {b.name} - {b.address}
            </option>
          ))}
        </select>
      </div>

      {/* Apartment */}
      <div>
        <label htmlFor="apartment" className="block text-sm font-medium text-gray-700">
          Apartment
        </label>
        <select
          id="apartment"
          value={apartmentId}
          onChange={(e) => setApartmentId(e.target.value)}
          disabled={!buildingId || availableApartments.length === 0}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm disabled:bg-gray-100 disabled:text-gray-500"
        >
          <option value="">Select an apartment (optional)</option>
          {availableApartments.map((a) => (
            <option key={a.id} value={a.id}>
              Unit {a.unit_number}
            </option>
          ))}
        </select>
      </div>

      {/* Description */}
      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700">
          Description <span className="text-red-500">*</span>
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={4}
          placeholder="Please provide detailed information about the issue..."
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          required
        />
      </div>

      {/* Photo Upload */}
      <div>
        <label htmlFor="photos" className="block text-sm font-medium text-gray-700">
          Photos (Cloudinary ready)
        </label>
        <input
          type="file"
          id="photos"
          accept="image/*"
          multiple
          onChange={handlePhotoChange}
          className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
        />
        {photos.length > 0 && (
          <p className="mt-2 text-sm text-gray-600">
            {photos.length} photo{photos.length !== 1 ? 's' : ''} selected
          </p>
        )}
      </div>

      {/* Submit Button */}
      <div>
        <button
          type="submit"
          disabled={!isValid || isSubmitting}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Submitting...
            </>
          ) : (
            'Submit Report'
          )}
        </button>
      </div>
    </form>
  );
}

export default ReportForm;
