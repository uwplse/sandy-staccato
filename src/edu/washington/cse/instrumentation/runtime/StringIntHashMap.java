/*
 * Copyright (c) 2000-2005, Dennis M. Sosnoski. All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 * 
 * Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer. Redistributions in binary
 * form must reproduce the above copyright notice, this list of conditions and
 * the following disclaimer in the documentation and/or other materials provided
 * with the distribution. Neither the name of JiBX nor the names of its
 * contributors may be used to endorse or promote products derived from this
 * software without specific prior written permission.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

package edu.washington.cse.instrumentation.runtime;

import java.util.Arrays;

public final class StringIntHashMap
{
    /** Default fill fraction allowed before growing table. */
    protected static final double DEFAULT_FILL = 0.3d;

    /** Minimum size used for hash table. */
    protected static final int MINIMUM_SIZE = 3;

    /** Fill fraction allowed for this hash table. */
    protected final double m_fillFraction;

    /** Number of entries present in table. */
    protected int m_entryCount;

    /** Entries allowed before growing table. */
    protected int m_entryLimit;

    /** Size of array used for keys. */
    protected int m_arraySize;

    /** Offset added (modulo table size) to slot number on collision. */
    protected int m_hitOffset;

    /** Array of key table slots. */
    protected String[] m_keyTable;

    /** Array of value table slots. */
    protected int[] m_valueTable;
    
    /** index into value table slots */
    protected int[] m_index;

    /**
     * Constructor with full specification.
     * 
     * @param count number of values to assume in initial sizing of table
     * @param fill fraction full allowed for table before growing
     * @param miss value returned when key not found in table
     */
    public StringIntHashMap(int count, double fill) {

        // check the passed in fill fraction
        if (fill <= 0.0d || fill >= 1.0d) {
            throw new IllegalArgumentException("fill value out of range");
        }
        m_fillFraction = fill;

        // compute initial table size (ensuring odd)
        m_arraySize = Math.max((int)(count / m_fillFraction), MINIMUM_SIZE);
        m_arraySize += (m_arraySize + 1) % 2;

        // initialize the table information
        m_entryLimit = (int)(m_arraySize * m_fillFraction);
        m_hitOffset = m_arraySize / 2;
        m_keyTable = new String[m_arraySize];
        m_valueTable = new int[m_arraySize];
        m_index = new int[m_arraySize];
    }

    /**
     * Constructor with only size supplied. Uses default hash technique and
     * values for fill fraction and value returned when key not found in table.
     * 
     * @param count number of values to assume in initial sizing of table
     */
    public StringIntHashMap(int count) {
        this(count, DEFAULT_FILL);
    }

    /**
     * Default constructor.
     */
    public StringIntHashMap() {
        this(0, DEFAULT_FILL);
    }

    /**
     * Copy (clone) constructor.
     * 
     * @param base instance being copied
     */
    public StringIntHashMap(StringIntHashMap base) {

        // copy the basic occupancy information
        m_fillFraction = base.m_fillFraction;
        m_entryCount = base.m_entryCount;
        m_entryLimit = base.m_entryLimit;
        m_arraySize = base.m_arraySize;
        m_hitOffset = base.m_hitOffset;

        // copy table of items
        m_keyTable = new String[m_arraySize];
        System.arraycopy(base.m_keyTable, 0, m_keyTable, 0, m_arraySize);
        m_valueTable = new int[m_arraySize];
        System.arraycopy(base.m_valueTable, 0, m_valueTable, 0, m_arraySize);
        m_index = new int[m_arraySize];
        System.arraycopy(base.m_index, 0, m_index, 0, m_arraySize);
    }

    /**
     * Step the slot number for an entry. Adds the collision offset (modulo
     * the table size) to the slot number.
     *
     * @param slot slot number to be stepped
     * @return stepped slot number
     */
    private final int stepSlot(int slot) {
        return (slot + m_hitOffset) % m_arraySize;
    }

    /**
     * Find free slot number for entry. Starts at the slot based directly
     * on the hashed key value. If this slot is already occupied, it adds
     * the collision offset (modulo the table size) to the slot number and
     * checks that slot, repeating until an unused slot is found.
     *
     * @param slot initial slot computed from key
     * @return slot at which entry was added
     */
    private final int freeSlot(int slot) {
        while (m_keyTable[slot] != null) {
            slot = stepSlot(slot);
        }
        return slot;
    }

    /**
     * Standard base slot computation for a key.
     *
     * @param key key value to be computed
     * @return base slot for key
     */
    private final int standardSlot(String key) {
        return (key.hashCode() & Integer.MAX_VALUE) % m_arraySize;
    }

    /**
     * Standard find key in table. This method may be used directly for key
     * lookup using either the <code>hashCode()</code> method defined for the
     * key objects or the <code>System.identityHashCode()</code> method, and
     * either the <code>equals()</code> method defined for the key objects or
     * the <code>==</code> operator, as selected by the hash technique
     * constructor parameter. To implement a hash class based on some other
     * methods of hashing and/or equality testing, define a separate method in
     * the subclass with a different name and use that method instead. This
     * avoids the overhead caused by overrides of a very heavily used method.
     *
     * @param key to be found in table
     * @return index of matching key, or <code>-index-1</code> of slot to be
     * used for inserting key in table if not already present (always negative)
     */
    private int standardFind(String key) {

        // find the starting point for searching table
        int slot = standardSlot(key);

        // scan through table to find target key
        while (m_keyTable[slot] != null) {

            // check if we have a match on target key
            if (m_keyTable[slot].equals(key)) {
                return slot;
            } else {
                slot = stepSlot(slot);
            }

        }
        return -slot-1;
    }

    /**
     * Restructure the table. This is used when the table is increasing or
     * decreasing in size, and works directly with the old table representation
     * arrays. It inserts pairs from the old arrays directly into the table
     * without adjusting the count present or checking the table size.
     * 
     * @param keys array of keys
     * @param values array of values
     */
    private void restructure(String[] keys, int[] values) {
    	int entryNum = 0;
        for (int i = 0; i < keys.length; i++) {
            if (keys[i] != null) {
                assignSlot(keys[i], values[i], entryNum++);
            }
        }
    }

    /**
     * Assign slot for entry. Starts at the slot found by the hashed key value.
     * If this slot is already occupied, it steps the slot number and checks the
     * resulting slot, repeating until an unused slot is found. This method does
     * not check for duplicate keys, so it should only be used for internal
     * reordering of the tables.
     * 
     * @param key to be added to table
     * @param value associated value for key
     * @param entryNum 
     * @return slot at which entry was added
     */
    private int assignSlot(String key, int value, int entryNum) {
        int offset = freeSlot(standardSlot(key));
        m_keyTable[offset] = key;
        m_valueTable[offset] = value;
        m_index[entryNum] = offset;
        return offset;
    }

    /**
     * Add an entry to the table. If the key is already present in the table,
     * this replaces the existing value associated with the key.
     * 
     * @param key key to be added to table (non- <code>null</code>)
     * @param value associated value for key
     * @return value previously associated with key, or reserved not found value
     * if key not previously present in table
     */
    public void add(String key, int value) {

        // first validate the parameters
        if (key == null) {
            throw new IllegalArgumentException("null key not supported");
        } 
        // check space available
        int min = m_entryCount + 1;
        if (min > m_entryLimit) {
            
            // find the array size required
            int size = m_arraySize;
            int limit = m_entryLimit;
            while (limit < min) {
                size = size * 2 + 1;
                limit = (int) (size * m_fillFraction);
            }
        
            // set parameters for new array size
            m_arraySize = size;
            m_entryLimit = limit;
            m_hitOffset = size / 2;
            
            // restructure for larger arrays
            String[] keys = m_keyTable;
            m_keyTable = new String[m_arraySize];
            int[] values = m_valueTable;
            m_valueTable = new int[m_arraySize];
            m_index = new int[m_arraySize];
            restructure(keys, values);
        }
        
        // find slot of table
        int offset = standardFind(key);
        if (offset >= 0) {

            // replace existing value for key
            m_valueTable[offset] = value;
            return;

        } else {

            // add new pair to table
            int indexOffs = m_entryCount++;
            offset = -offset - 1;
            m_keyTable[offset] = key;
            m_valueTable[offset] = value;
            m_index[indexOffs] = offset;
            return;

        }
    }

    /**
     * Check if an entry is present in the table. This method is supplied to
     * support the use of values matching the reserved not found value.
     * 
     * @param key key for entry to be found
     * @return <code>true</code> if key found in table, <code>false</code>
     * if not
     */
    public final boolean containsKey(String key) {
        return standardFind(key) >= 0;
    }

    /**
     * Find an entry in the table.
     * 
     * @param key key for entry to be returned
     * @return value for key, or reserved not found value if key not found
     */
    public final int get(String key) {
        int slot = standardFind(key);
        if (slot >= 0) {
            return m_valueTable[slot];
        } else {
            throw new RuntimeException();
        }
    }

    /**
     * Construct a copy of the table.
     * 
     * @return shallow copy of table
     */
    @Override
		public Object clone() {
        return new StringIntHashMap(this);
    }

		public boolean isEmpty() {
			return m_entryCount == 0;
		}
		
		public String debugToString() {
			return "StringIntHashMap [m_entryCount=" + m_entryCount + ", m_keyTable="
					+ Arrays.toString(m_keyTable) + ", m_valueTable="
					+ Arrays.toString(m_valueTable) + ", m_index="
					+ Arrays.toString(m_index) + "]";
		}
		
		@Override
		public boolean equals(Object o) {
			if(o == null) {
				return false;
			}
			if(!(o instanceof StringIntHashMap)) {
				return false;
			}
			StringIntHashMap other = (StringIntHashMap)o;
			if(other.m_entryCount != this.m_entryCount) {
				return false;
			}
			for(int i = 0; i < this.m_entryCount; i++) {
				int vIndex = this.m_index[i];
				String key = this.m_keyTable[vIndex];
				int value = this.m_valueTable[vIndex];
				if(!other.containsKey(key) || other.get(key) != value) {
					return false;
				}
			}
			return true;
		}

		@Override
		public String toString() {
			StringBuilder builder = new StringBuilder();
			builder.append('{');
			boolean first = true;
			for(int i = 0; i < this.m_entryCount; i++) {
				if(!first) {
					builder.append(", ");
				}
				builder.append(this.m_keyTable[this.m_index[i]]).append('=');
				builder.append(this.m_valueTable[this.m_index[i]]);
				first = false;
			}
			builder.append('}');
			return builder.toString();
		}
}
